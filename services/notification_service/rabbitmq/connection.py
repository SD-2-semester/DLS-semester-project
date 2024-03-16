import json
import pika
from api.routes.notifications.ws_connection_manager import ws_manager


def get_rabbitmq_connection():
    # Assuming RabbitMQ is running with default settings in a local Docker container
    try:
        credentials = pika.PlainCredentials("user", "password")
        parameters = pika.ConnectionParameters("localhost", 5672, "/", credentials)
        connection = pika.BlockingConnection(parameters)
        return connection
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        raise


def rabbitmq_consumer():
    connection = get_rabbitmq_connection()
    print("connected")
    channel = connection.channel()

    channel.queue_declare(queue="new_relation_queue", durable=True)

    def callback(ch, method, properties, body):
        message = json.loads(body)
        print(message)
        user_id_1 = message.get("user_id_1")
        user_id_2 = message.get("user_id_2")

        print(ws_manager.active_connections)
        # Broadcasting to user_id_1 and user_id_2
        if user_id_1 in ws_manager.active_connections:
            ws_manager.broadcast(f"Notification for user: {user_id_1}", user_id_1)
        if user_id_2 in ws_manager.active_connections:
            ws_manager.broadcast(f"Notification for user: {user_id_2}", user_id_2)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue="new_relation_queue", on_message_callback=callback, auto_ack=False
    )

    print("Started consuming")
    channel.start_consuming()
