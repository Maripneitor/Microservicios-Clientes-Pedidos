import os
import pika
import json

from app.application.ports import MessengerPort

class PikaMessenger(MessengerPort):
    def __init__(self):
        self.rabbitmq_url = os.getenv("RABBITMQ_URL")

    def publish_order_event(self, order_data: dict):
        params = pika.URLParameters(self.rabbitmq_url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='order_notifications', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='order_notifications',
            body=json.dumps(order_data),
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        connection.close()
