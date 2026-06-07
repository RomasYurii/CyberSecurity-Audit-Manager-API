from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/cyber_audit"

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