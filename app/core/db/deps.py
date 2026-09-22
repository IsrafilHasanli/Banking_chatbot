from app.core.db.database import async_session_local

async def get_db():
    async with async_session_local() as session:
        yield session