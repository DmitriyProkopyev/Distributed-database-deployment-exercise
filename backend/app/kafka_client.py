from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.config import settings
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class KafkaClient:
    def __init__(self):
        self.producer = None
        self.consumer = None
        
    async def connect(self, max_retries=5, retry_delay=5):
        for attempt in range(max_retries):
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'))
                await self.producer.start()
                logger.info("Successfully connected to Kafka")
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to connect to Kafka after {max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"Attempt {attempt + 1} failed to connect to Kafka: {str(e)}. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
        
    async def close(self):
        if self.producer:
            await self.producer.stop()
            
    async def send_message(self, topic: str, message: dict):
        await self.producer.send_and_wait(topic, message)

kafka_client = KafkaClient()
