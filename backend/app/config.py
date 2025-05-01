from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://mongo:27017"
    MONGO_DB_NAME: str = "testdb"
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_TOPIC_NGINX_TO_BACKEND: str = "nginx_requests"
    KAFKA_TOPIC_BACKEND_TO_DB: str = "write_data"
    KAFKA_TOPIC_DB_RESPONSES: str = "data"
    
    class Config:
        env_file = ".env"

settings = Settings()
