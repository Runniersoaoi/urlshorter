from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from database import init_db, get_db
from schemas import URLCreate, URLResponse, URLStatsResponse
from crud import create_url, get_url_by_short_id, create_url_stats, get_url_stats
from redis_client import get_redis
import redis.asyncio as redis
import httpx
import os

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://ml_service:8000")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="URL Shortener API", lifespan=lifespan)


# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- ML CHECK ----------------
async def check_safe_url(url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{ML_SERVICE_URL}/predict",
                                         json={"url": url},
                                         timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                if not data.get("safe", True):
                    raise HTTPException(status_code=422, detail="URL detected as unsafe")
    except httpx.RequestError:
        print("ML Service unavailable, skipping check.")


# ---------------- RATE LIMIT MIDDLEWARE ----------------
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host

    # Obtener cliente Redis desde el async generator
    redis_gen = get_redis()
    redis_client = await redis_gen.__anext__()

    key = f"rate_limit:{client_ip}"

    try:
        current = await redis_client.incr(key)
        if current == 1:
            await redis_client.expire(key, 1)

        if current > 5:
            raise HTTPException(status_code=429, detail="Too many requests")

    except Exception as e:
        # Si Redis falla, no detenemos la API
        print(f"[Rate Limit] Redis error: {e}")

    response = await call_next(request)
    return response


# ---------------- ENDPOINTS ----------------

@app.post("/shorten", response_model=URLResponse)
async def shorten_url(
    url: URLCreate,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    await check_safe_url(str(url.original_url))

    db_url = await create_url(db, url)

    # Cache it (fail silently if Redis is down)
    try:
        await redis_client.set(f"url:{db_url.short_id}",
                               str(db_url.original_url),
                               ex=86400)
    except Exception as e:
        print(f"[Cache] Redis error: {e}")
    
    return db_url


@app.get("/{short_id}")
async def redirect_to_url(
    short_id: str,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    # Try cache first
    try:
        cached_url = await redis_client.get(f"url:{short_id}")
    except Exception as e:
        print(f"[Cache] Redis error: {e}")
        cached_url = None
    
    if cached_url:
        original_url = cached_url
    else:
        db_url = await get_url_by_short_id(db, short_id)
        if not db_url:
            raise HTTPException(status_code=404, detail="URL not found")

        original_url = db_url.original_url
        
        try:
            await redis_client.set(f"url:{short_id}", str(original_url), ex=86400)
        except Exception as e:
            print(f"[Cache] Redis error: {e}")

    background_tasks.add_task(
        create_url_stats,
        db,
        short_id,
        ip=request.client.host,
        country="Unknown",
        browser=request.headers.get("User-Agent"),
        os="Unknown",
        device="Unknown",
        referrer=request.headers.get("Referer")
    )

    return RedirectResponse(url=original_url)


@app.get("/stats/{short_id}", response_model=URLStatsResponse)
async def get_stats(short_id: str, db: AsyncSession = Depends(get_db)):
    stats = await get_url_stats(db, short_id)
    return stats


@app.get("/health")
async def health_check():
    return {"status": "ok"}
