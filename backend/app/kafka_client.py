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
        if self.consumer:
            await self.consumer.stop()

    async def send_message(self, topic: str, message: dict):
        await self.producer.send_and_wait(topic, message)

    async def _consume_responses(self):
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_TOPIC_DB_RESPONSES,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="backend_response_consumer",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        await self.consumer.start()
        try:
            async for msg in self.consumer:
                value = msg.value
                request_id = value.get("request_id")
                if request_id and request_id in self.response_futures:
                    future = self.response_futures.pop(request_id)
                    if not future.done():
                        future.set_result(value)
        finally:
            await self.consumer.stop()

    async def wait_for_response(self, request_id: str, timeout: float = 15.0):
        future = asyncio.get_event_loop().create_future()
        self.response_futures[request_id] = future
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            self.response_futures.pop(request_id, None)
            raise

kafka_client = KafkaClient()
