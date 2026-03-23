import os
import pika
import json
import time
from app.infrastructure.db.repository import SqlAlchemyClientRepository
from app.application.use_cases import UpdateClientStatsUseCase

def rabbitmq_listener(session_factory):
    rabbitmq_url = os.getenv("RABBITMQ_URL")
    params = pika.URLParameters(rabbitmq_url)
    
    while True:
        try:
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue='order_notifications', durable=True)

            def callback(ch, method, properties, body):
                data = json.loads(body)
                print(f"Received order notification: {data}")
                
                db = session_factory()
                try:
                    repository = SqlAlchemyClientRepository(db)
                    use_case = UpdateClientStatsUseCase(repository)
                    use_case.execute(data['client_id'])
                finally:
                    db.close()
                    
                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue='order_notifications', on_message_callback=callback)
            print("Clients service listening for RabbitMQ messages...")
            channel.start_consuming()
            break
        except Exception as e:
            print(f"Waiting for RabbitMQ... Error: {e}")
            time.sleep(5)
