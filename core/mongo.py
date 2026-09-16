from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

class MongoManager:
    client: AsyncIOMotorClient = None
    db = None

mongo_db = MongoManager()

async def connect_to_mongo():
    try:
        mongo_db.client = AsyncIOMotorClient(settings.MONGO_URL)
        mongo_db.db = mongo_db.client[settings.MONGO_DB_NAME]
        await mongo_db.client.admin.command('ping')
        print("✓ Conexión exitosa a MongoDB Atlas")
    except Exception as e:
        print(f"✗ Error conectando a MongoDB Atlas: {e}")
        raise e

async def close_mongo_connection():
    if mongo_db.client:
        mongo_db.client.close()
        print("✓ Conexión a MongoDB Atlas cerrada")

def get_mongo_db():
    return mongo_db.db