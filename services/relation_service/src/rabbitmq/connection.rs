use crate::dao;
use crate::dtos::user_dtos::UserInputDTO;
use actix_web::web;
use bcrypt::hash;
use deadpool_lapin::lapin::protocol::channel;
use dotenv::dotenv;
use futures::future::err;
use lapin::{
    message::DeliveryResult,
    options::{
        BasicAckOptions, BasicConsumeOptions, BasicPublishOptions,
        ExchangeDeclareOptions, QueueDeclareOptions,
    },
    types::FieldTable,
    BasicProperties, Channel, Connection, ConnectionProperties, Consumer, ExchangeKind,
};
use neo4rs::Graph;
use serde::Serialize;
use serde_json::to_vec;
use std::env;

/// Contruct uri
pub async fn create_amqp_uri() -> String {
    dotenv().ok(); // Load .env file

    let user = env::var("AMQP_USER").unwrap_or_else(|_| "user".to_string());
    let password = env::var("AMQP_PASSWORD").unwrap_or_else(|_| "password".to_string());
    let host = env::var("AMQP_HOST").unwrap_or_else(|_| "localhost".to_string());
    let port = env::var("AMQP_PORT").unwrap_or_else(|_| "5672".to_string());

    format!("amqp://{}:{}@{}:{}", user, password, host, port)
}

/// Create connection to rabbitmq, and return the connection.
pub async fn get_connection() -> Connection {
    let uri = create_amqp_uri().await;
    let options = ConnectionProperties::default()
        // Use tokio executor and reactor.
        // At the moment the reactor is only available for unix.
        .with_executor(tokio_executor_trait::Tokio::current())
        .with_reactor(tokio_reactor_trait::Tokio);

    Connection::connect(&uri, options).await.unwrap()
}

/// Create channel to a given connection.
pub async fn channel_rabbitmq(connection: &Connection) -> Channel {
    connection.create_channel().await.unwrap()
}

/// Create a queue if it doesn't exist. Durable set to true.
pub async fn create_queue(channel: &Channel, queue_name: &str) {
    let queue_options = QueueDeclareOptions {
        durable: true,
        ..Default::default()
    };

    let _queue = channel
        .queue_declare(queue_name, queue_options, FieldTable::default())
        .await
        .unwrap();
}

pub async fn create_exchange(channel: &Channel, exchange_name: &str) {
    let exchange_options = ExchangeDeclareOptions {
        durable: true,
        ..Default::default()
    };

    let _queue = channel
        .exchange_declare(
            exchange_name,
            ExchangeKind::Fanout,
            exchange_options,
            FieldTable::default(),
        )
        .await
        .unwrap();
}

/// Create a consumer.
pub async fn create_consumer(channel: &Channel, queue_name: &str) -> Consumer {
    let tag = format!("tag_{}", queue_name);

    channel
        .basic_consume(
            queue_name,
            &tag,
            BasicConsumeOptions::default(),
            FieldTable::default(),
        )
        .await
        .unwrap()
}

/// Create a publisher, that can publish serde structs.
pub async fn publish_to_queue<T: Serialize>(
    channel: &Channel,
    queue_name: &str,
    data: &T,
) {
    let payload = to_vec(data).expect("Failed to serialize data");

    channel
        .basic_publish(
            "",
            queue_name,
            BasicPublishOptions::default(),
            &payload,
            BasicProperties::default(),
        )
        .await
        .unwrap()
        .await
        .unwrap();
}
/// Just for testing if message gets consumed
pub async fn print_result(consumer: &Consumer) {
    consumer.set_delegate(move |delivery: DeliveryResult| async move {
        let delivery = match delivery {
            Ok(Some(delivery)) => delivery,
            Ok(None) => return,
            Err(error) => {
                dbg!("Failed to consume queue message {}", error);
                return;
            }
        };

        if let Ok(payload) = std::str::from_utf8(&delivery.data) {
            println!("Received message: {}", payload);
        }

        delivery
            .ack(BasicAckOptions::default())
            .await
            .expect("Failed to ack send_webhook_event message");
    });
}

/// Create a new user in the database, by consuming message.
/// We use db from app state.
pub async fn create_new_user(
    consumer: &Consumer,
    db: web::Data<Graph>,
    channel: Channel,
) {
    let error_queue: &str = "new_user_error_queue";

    consumer.set_delegate(move |delivery: DeliveryResult| {
        let db_clone = db.clone();
        let channel_clone = channel.clone();
        async move {
            let delivery = match delivery {
                Ok(Some(delivery)) => delivery,
                Ok(None) => return,
                Err(error) => {
                    dbg!("Failed to consume queue message {}", error);

                    return;
                }
            };
            
            if let Ok(payload_str) = std::str::from_utf8(&delivery.data) {
                match serde_json::from_str::<UserInputDTO>(payload_str) {
                    Ok(user_input_dto) => {
                        match dao::user_dao::create_node(&db_clone, user_input_dto)
                            .await
                        {
                            Ok(Some(user_id)) => {
                                println!("User created with ID: {:?}", user_id);
                            }
                            Ok(None) => {
                                println!("User creation failed: No ID returned");
                                publish_to_queue(
                                    &channel_clone,
                                    error_queue,
                                    &delivery.data,
                                )
                                .await;
                            }
                            Err(err) => {
                                println!("Database error occurred: {:?}", err);
                                publish_to_queue(
                                    &channel_clone,
                                    error_queue,
                                    &delivery.data,
                                )
                                .await;
                            }
                        }
                    }
                    Err(err) => {
                        println!("Error deserializing user input: {:?}", err);
                        publish_to_queue(&channel_clone, error_queue, &delivery.data)
                            .await;
                    }
                }
            }

            delivery
                .ack(BasicAckOptions::default())
                .await
                .expect("Failed to ack send_webhook_event message");
        }
    });
}
