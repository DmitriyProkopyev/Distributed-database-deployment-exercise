from app.database import mongodb
from app.kafka_client import kafka_client
from app.config import settings
from app.utils import to_json, validate_id
import asyncio

async def handle_db_command(message: dict):
    col = mongodb.get_collection()
    try:
        action = message.get("action")
        
        if action == "create":
            result = await col.insert_one(message["data"])
            response = {"id": str(result.inserted_id)}
            
        elif action == "read_one":
            doc = await col.find_one({"_id": validate_id(message["doc_id"])})
            response = {to_json(doc) if doc else {}}
            
        elif action == "read_many":
            cursor = col.find().skip(message.get("skip", 0)).limit(message.get("limit", 100))
            docs = await cursor.to_list(length=message.get("limit", 100))
            response = {to_json(docs)}
            
        elif action == "update":
            result = await col.update_one(
                {"_id": validate_id(message["doc_id"])},
                {"$set": message["data"]}
            )
            response = {"status": "success"}
            
        elif action == "delete":
            result = await col.delete_one({"_id": validate_id(message["doc_id"])})
            response = {"status": "success"}
            
        else:
            response = {"error": "unknown action"}
            
        return response
        
    except Exception as e:
        return {"error": str(e)}

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
            if "request_id" in response:
                await kafka_client.send_message(settings.KAFKA_TOPIC_DB_RESPONSES, response)
    finally:
        await consumer.stop()
