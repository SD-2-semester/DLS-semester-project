use crate::dao;
use crate::dtos::user_dtos::UserInputDTO;
use lapin::{
    message::DeliveryResult,
    options::{BasicAckOptions, BasicConsumeOptions, BasicPublishOptions, QueueDeclareOptions},
    types::FieldTable,
    BasicProperties, Channel, Connection, ConnectionProperties, Consumer,
};
use neo4rs::Graph;
use serde::{de::IntoDeserializer, Serialize};
use serde_json::to_vec;

pub async fn get_connection() -> Connection {
    let uri = "amqp://user:password@localhost:5672";
    let options = ConnectionProperties::default()
        // Use tokio executor and reactor.
        // At the moment the reactor is only available for unix.
        .with_executor(tokio_executor_trait::Tokio::current())
        .with_reactor(tokio_reactor_trait::Tokio);

    return Connection::connect(uri, options).await.unwrap();
}

pub async fn channel_rabbitmq(connection: &Connection) -> Channel {
    let channel = connection.create_channel().await.unwrap();
    return channel;
}

pub async fn create_queue(channel: &Channel, queue_name: &str) {
    let _queue = channel
        .queue_declare(
            queue_name,
            QueueDeclareOptions::default(),
            FieldTable::default(),
        )
        .await
        .unwrap();
}

pub async fn create_consumer(channel: &Channel, queue_name: &str) -> Consumer {
    let tag = format!("tag_{}", queue_name);
    let consumer = channel
        .basic_consume(
            queue_name,
            &tag,
            BasicConsumeOptions::default(),
            FieldTable::default(),
        )
        .await
        .unwrap();

    return consumer;
}

pub async fn publish_to_queue<T: Serialize>(channel: &Channel, queue_name: &str, data: &T) {
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

pub async fn create_new_user(consumer: &Consumer, db: &Graph) {
    consumer.set_delegate(move |delivery: DeliveryResult| async move {
        let delivery = match delivery {
            Ok(Some(delivery)) => delivery,
            Ok(None) => return,
            Err(error) => {
                dbg!("Failed to consume queue message {}", error);
                return;
            }
        };
        if let Ok(payload_str) = std::str::from_utf8(&delivery.data) {
            if let Ok(user_input_dto) = serde_json::from_str::<UserInputDTO>(payload_str) {
                dao::user_dao::create_node(&db, user_input_dto).await;
            }
        }

        delivery
            .ack(BasicAckOptions::default())
            .await
            .expect("Failed to ack send_webhook_event message");
    });
}
