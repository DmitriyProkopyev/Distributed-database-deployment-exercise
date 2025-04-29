from fastapi import FastAPI
from app.database import mongodb
from app.kafka_client import kafka_client
from app.db_consumer import start_db_consumer
import asyncio

app = FastAPI(title="Distributed Database Deployment")

@app.on_event("startup")
async def startup():
    await mongodb.connect()
    await kafka_client.connect()
    asyncio.create_task(start_db_consumer())

@app.on_event("shutdown")
async def shutdown():
    await mongodb.close()
    await kafka_client.close()

@app.post("/create_document/")
async def create_document(data: dict):
    from app.services import create_doc
    return await create_doc(data)

@app.get("/read_documents/")
async def read_documents(skip: int = 0, limit: int = 100):
    from app.services import get_docs
    return await get_docs(skip=skip, limit=limit)

@app.get("/read_document/{doc_id}")
async def read_document(doc_id: str):
    from app.services import get_doc
    return await get_doc(doc_id)

@app.put("/update_document/{doc_id}")
async def update_document(doc_id: str, data: dict):
    from app.services import update_doc
    return await update_doc(doc_id, data)

@app.delete("/delete_document/{doc_id}")
async def delete_document(doc_id: str):
    from app.services import delete_doc
    return await delete_doc(doc_id)

@app.get("/check_health")
async def check_health():
    from app.services import health_check
    return await health_check()
