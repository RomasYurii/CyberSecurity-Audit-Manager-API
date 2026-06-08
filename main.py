from contextlib import asynccontextmanager
from fastapi import FastAPI
from database.database import engine
from database.models import Base
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from security.security import limiter
from router import login, register, targets
from database import models
from contextlib import asynccontextmanager
from fastapi import FastAPI

from database.database import engine, Base
from database import models  # !!! ОБОВ'ЯЗКОВО ІМПОРТУЄМО ВЕСЬ ФАЙЛ МОДЕЛЕЙ !!!

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Коли викликається create_all, SQLAlchemy дивиться у Base.metadata.
    # Завдяки імпорту вище, там уже будуть таблиці users, targets тощо.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="CyberSecurity Audit Manager", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(login.router, tags=["login"])
app.include_router(register.router, tags=["register"])
app.include_router(targets.router, tags=["targets"])