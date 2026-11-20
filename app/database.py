import os
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "blogging_db")

client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGODB_URL,
    serverSelectionTimeoutMS=5000
)

database = client[DATABASE_NAME]
users_collection = database["users"]
blogs_collection = database["blogs"]
categories_collection = database["categories"]
