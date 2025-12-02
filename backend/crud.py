from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import URL, URLStats, User
from schemas import URLCreate, UserCreate
from utils import generate_short_id
from auth import get_password_hash
from datetime import datetime
import uuid


async def create_url(db: AsyncSession, url: URLCreate, user_id: int = None) -> URL:
    # 1) Generar un short_id temporal único para pasar la restricción NOT NULL
    # Usamos UUID para evitar colisiones durante el flush
    temp_short_id = f"temp_{uuid.uuid4().hex[:8]}"
    
    db_url = URL(
        original_url=str(url.original_url),
        short_id=temp_short_id,
        user_id=user_id
    )
    db.add(db_url)

    # 2) Generar el ID (el flush ahora funcionará porque short_id no es null)
    await db.flush()

    # 3) Actualizar con el verdadero short_id basado en el ID generado
    db_url.short_id = generate_short_id(db_url.id)
    
    # 4) Guardar cambios finales
    await db.commit()
    await db.refresh(db_url)
    
    return db_url


async def get_url_by_short_id(db: AsyncSession, short_id: str) -> URL | None:
    result = await db.execute(select(URL).where(URL.short_id == short_id))
    return result.scalars().first()


async def create_url_stats(
    db: AsyncSession,
    short_id: str,
    ip: str = None,
    country: str = None,
    browser: str = None,
    os: str = None,
    device: str = None,
    referrer: str = None
):
    stats = URLStats(
        short_id=short_id,
        ip=ip,
        country=country,
        browser=browser,
        os=os,
        device=device,
        referrer=referrer
    )
    db.add(stats)
    await db.commit()


async def get_url_stats(db: AsyncSession, short_id: str):
    result = await db.execute(select(URLStats).where(URLStats.short_id == short_id))
    stats = result.scalars().all()

    total_clicks = len(stats)
    browsers = {}
    countries = {}
    os_systems = {}
    referrers = {}

    for s in stats:
        browsers[s.browser] = browsers.get(s.browser, 0) + 1
        countries[s.country] = countries.get(s.country, 0) + 1
        os_systems[s.os] = os_systems.get(s.os, 0) + 1
        referrers[s.referrer] = referrers.get(s.referrer, 0) + 1

    return {
        "total_clicks": total_clicks,
        "browsers": browsers,
        "countries": countries,
        "os": os_systems,
        "referrers": referrers
    }

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, password_hash=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_urls(db: AsyncSession, user_id: int):
    result = await db.execute(select(URL).where(URL.user_id == user_id))
    return result.scalars().all()
