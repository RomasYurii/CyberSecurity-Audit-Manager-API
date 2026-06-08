from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")

# Створюємо асинхронний рушій
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Створюємо фабрику асинхронних сесій
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

# Залежність тепер теж асинхронна
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session