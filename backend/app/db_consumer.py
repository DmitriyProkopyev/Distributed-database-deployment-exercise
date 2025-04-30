from app.database import mongodb
from app.kafka_client import kafka_client
from app.config import settings
from app.utils import to_json, validate_id
from aiokafka import AIOKafkaConsumer
import json
import asyncio

async def handle_db_command(message: dict):
    col = mongodb.get_collection()
    try:
        action = message.get("action")
        request_id = message.get("request_id")
        
        if action == "create":
            data = message["data"]
            if "_id" in data:
                await col.replace_one({"_id": validate_id(data["_id"])}, data, upsert=True)
                response = {"id": str(data["_id"]), "request_id": request_id}
            else:
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
            
        return response
        
    except Exception as e:
        return {"error": str(e), "request_id": request_id}

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
