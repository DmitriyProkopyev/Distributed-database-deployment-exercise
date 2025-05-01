from app.database import mongodb
from app.kafka_client import kafka_client
from app.config import settings
from app.utils import to_json, validate_id
from aiokafka import AIOKafkaConsumer
import datetime
import json
import asyncio

async def handle_db_command(message: dict):
    processed_col = mongodb.get_processed_requests_collection()
    request_id = message.get("request_id")
    existing = await processed_col.find_one({"_id": request_id})
    if existing:
        return existing["response"]

    col = mongodb.get_collection()
    response = None
    try:
        action = message.get("action")
        
        if action == "create":
            data = message["data"]
            result = await col.insert_one(data)
            response = {"id": str(result.inserted_id), "request_id": request_id}
                
        elif action == "read":
            if "doc_id" in message:
                doc = await col.find_one({"_id": validate_id(message["doc_id"])})
                response = {"data": to_json(doc) if doc else {}, "request_id": request_id}
            else:
                cursor = col.find().skip(message.get("skip", 0)).limit(message.get("limit", 100))
                docs = await cursor.to_list(length=message.get("limit", 100))
                response = {"data": to_json(docs), "request_id": request_id}
                
        elif action == "update":
            await col.replace_one(
                {"_id": validate_id(message["doc_id"])},
                message["data"],
                upsert=True
            )
            response = {"status": "success", "request_id": request_id}
            
        else:
            response = {"error": "unknown action", "request_id": request_id}

        if response:
            await processed_col.insert_one({
                "_id": request_id,
                "response": response,
                "action": action,
                "timestamp": datetime.datetime.utcnow()
            })
            
        return response
        
    except Exception as e:
        error_response = {"error": str(e), "request_id": request_id}
        await processed_col.insert_one({
            "_id": request_id,
            "response": error_response,
            "action": action,
            "timestamp": datetime.datetime.utcnow()
        })
        return error_response

async def start_db_consumer():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC_BACKEND_TO_DB,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="db_consumer_group",
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    
    await consumer.start()
    try:
        async for msg in consumer:
            response = await handle_db_command(msg.value)
            await kafka_client.send_message(settings.KAFKA_TOPIC_DB_RESPONSES, response)
    finally:
        await consumer.stop()
