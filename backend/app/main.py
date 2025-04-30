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

@app.post("/documents/")
async def create_document(data: dict):
    return await create_doc(data)

@app.get("/documents/")
async def read_documents(skip: int = 0, limit: int = 100):
    return await get_docs(skip=skip, limit=limit)

@app.get("/documents/{doc_id}")
async def read_document(doc_id: str):
    return await get_doc(doc_id)

@app.put("/documents/{doc_id}")
async def update_document(doc_id: str, data: dict):
    return await update_doc(doc_id, data)

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    return await delete_doc(doc_id)

@app.get("/health")
async def check_health():
    return await health_check()
