from contextlib import asynccontextmanager
from fastapi import FastAPI
from database.database import engine
from database.models import Base
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from security.security import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

app = FastAPI(
    title = "CS API",
    description="API service for CS project",
    version="1.0",
    root_path= "/api/v1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
