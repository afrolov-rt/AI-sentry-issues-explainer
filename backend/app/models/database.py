from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def connect_to_mongo():
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URI)
        db.database = db.client[settings.DATABASE_NAME]
        
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        await create_indexes()
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

async def create_indexes():
    try:
        await db.database.processed_issues.create_index("sentry_issue.id")
        await db.database.processed_issues.create_index("workspace_id")
        await db.database.processed_issues.create_index([("sentry_issue.id", 1), ("workspace_id", 1)], unique=True)
        await db.database.processed_issues.create_index("status")
        await db.database.processed_issues.create_index("created_by")
        await db.database.processed_issues.create_index("assigned_to")
        await db.database.processed_issues.create_index("created_at")
        
        await db.database.users.create_index("username", unique=True)
        await db.database.users.create_index("email", unique=True)
        await db.database.users.create_index("workspace_id")
        
        await db.database.workspaces.create_index("owner_id")
        await db.database.workspaces.create_index("name")
        
        await db.database.settings.create_index("workspace_id", unique=True)
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")

def get_database():
    return db.database
