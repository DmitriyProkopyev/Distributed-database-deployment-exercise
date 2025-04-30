from fastapi import HTTPException
from app.database import mongodb
from app.kafka_client import kafka_client
from app.config import settings
from app.utils import to_json, validate_id
import uuid
import json
from aiokafka import AIOKafkaConsumer

async def wait_for_kafka_response(request_id: str, timeout: float = 5.0):
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC_DB_RESPONSES,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=f"response_consumer_{request_id}",
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=False
    )
    
    try:
        await consumer.start()
        while True:
            msg = await consumer.getone(timeout_ms=int(timeout*1000))
            if msg.value.get("request_id") == request_id:
                return msg.value
    except Exception as e:
        raise HTTPException(504, f"Timeout waiting for response: {str(e)}")
    finally:
        await consumer.stop()

async def create_doc(data: dict) -> dict:
    request_id = str(uuid.uuid4())
    await kafka_client.send_message(
        settings.KAFKA_TOPIC_BACKEND_TO_DB,
        {"action": "create", "data": data, "request_id": request_id}
    )
    response = await wait_for_kafka_response(request_id)
    if "error" in response:
        raise HTTPException(500, f"Document creation failed: {response['error']}")
    return await get_doc(response["id"])

async def get_doc(doc_id: str) -> dict:
    request_id = str(uuid.uuid4())
    await kafka_client.send_message(
        settings.KAFKA_TOPIC_BACKEND_TO_DB,
        {"action": "read", "doc_id": doc_id, "request_id": request_id}
    )
    response = await wait_for_kafka_response(request_id)
    if "error" in response:
        raise HTTPException(500, f"Document fetch failed: {response['error']}")
    if not response.get("data"):
        raise HTTPException(404, "Document not found")
    return to_json(response["data"])

async def get_docs(skip: int = 0, limit: int = 100) -> list[dict]:
    request_id = str(uuid.uuid4())
    await kafka_client.send_message(
        settings.KAFKA_TOPIC_BACKEND_TO_DB,
        {"action": "read", "skip": skip, "limit": limit, "request_id": request_id}
    )
    response = await wait_for_kafka_response(request_id)
    if "error" in response:
        raise HTTPException(500, f"Documents fetch failed: {response['error']}")
    return to_json(response.get("data", []))

async def update_doc(doc_id: str, data: dict) -> dict:
    request_id = str(uuid.uuid4())
    await kafka_client.send_message(
        settings.KAFKA_TOPIC_BACKEND_TO_DB,
        {"action": "update", "doc_id": doc_id, "data": data, "request_id": request_id}
    )
    response = await wait_for_kafka_response(request_id)
    if "error" in response:
        raise HTTPException(500, f"Document update failed: {response['error']}")
    return await get_doc(doc_id)

async def delete_doc(doc_id: str) -> dict:
    request_id = str(uuid.uuid4())
    await kafka_client.send_message(
        settings.KAFKA_TOPIC_BACKEND_TO_DB,
        {"action": "delete", "doc_id": doc_id, "request_id": request_id}
    )
    response = await wait_for_kafka_response(request_id)
    if "error" in response:
        raise HTTPException(500, f"Document deletion failed: {response['error']}")
    return {"status": "success"}

async def health_check() -> dict:
    try:
        request_id = str(uuid.uuid4())
        await kafka_client.send_message(
            settings.KAFKA_TOPIC_BACKEND_TO_DB,
            {"action": "health_check", "request_id": request_id}
        )
        response = await wait_for_kafka_response(request_id, timeout=2.0)
        return {"status": "healthy", "kafka": "ok", "mongo": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
