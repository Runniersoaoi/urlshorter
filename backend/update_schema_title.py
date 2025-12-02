import asyncio
from sqlalchemy import text
from database import engine

async def update_schema():
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE urls ADD COLUMN title VARCHAR;"))
            print("Added title column to urls table.")
        except Exception as e:
            print(f"Column title might already exist: {e}")

if __name__ == "__main__":
    asyncio.run(update_schema())
