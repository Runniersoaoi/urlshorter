import asyncio
from sqlalchemy import text
from database import engine

async def update_schema():
    async with engine.begin() as conn:
        # Create users table if not exists (handled by create_all usually, but let's be sure)
        # Actually, let's just add the column to urls if it's missing.
        # We can try to add it and ignore error if it exists, or check first.
        # Simple approach: Try to add it.
        try:
            await conn.execute(text("ALTER TABLE urls ADD COLUMN user_id INTEGER REFERENCES users(id);"))
            print("Added user_id column to urls table.")
        except Exception as e:
            print(f"Column user_id might already exist or users table missing: {e}")

if __name__ == "__main__":
    asyncio.run(update_schema())
