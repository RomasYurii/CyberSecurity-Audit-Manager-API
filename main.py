from router import login, register, targets, vulnerabilities, users, statistics
from contextlib import asynccontextmanager
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from limiter import limiter
from database.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    #async with engine.begin() as conn:
    #    await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="CyberSecurity Audit Manager API", lifespan=lifespan, version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login.router, tags=["login"])
app.include_router(register.router, tags=["register"])
app.include_router(targets.router, tags=["targets"])
app.include_router(vulnerabilities.router, tags=["vulnerabilities"])
app.include_router(users.router, tags=["users"])
app.include_router(statistics.router, tags=["statistics"])