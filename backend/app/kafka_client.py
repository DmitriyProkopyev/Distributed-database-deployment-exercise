from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.config import settings
import json

class KafkaClient:
    def __init__(self):
        self.producer = None
        self.consumer = None
        
    async def connect(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        await self.producer.start()
        
    async def close(self):
        if self.producer:
            await self.producer.stop()
            
    async def send_message(self, topic: str, message: dict):
        await self.producer.send_and_wait(topic, message)

kafka_client = KafkaClient()
