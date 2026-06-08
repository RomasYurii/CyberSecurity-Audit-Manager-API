# CyberSecurity Audit Manager API 
Async REST API for managing pentest targets, vulnerabilities, and reports.

**Tech:** Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Docker, JWT.

## Quick Start
1. Clone the repository.
2. Create `.env` file:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@db:5432/dbname
3. Run Docker:
    ```Bash

    docker-compose up -d --build

4. Apply migrations:
    ```Bash

    docker-compose exec api alembic upgrade head

Docs: http://127.0.0.1:8000/docs
