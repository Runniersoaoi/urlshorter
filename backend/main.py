from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from database import init_db, get_db
from schemas import URLCreate, URLResponse, URLStatsResponse
from crud import create_url, get_url_by_short_id, create_url_stats, get_url_stats, update_url, delete_url
from redis_client import get_redis
import redis.asyncio as redis
import httpx
import os
import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse
from user_agents import parse
import aiohttp
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import verify_password, create_access_token, get_password_hash
from jose import JWTError, jwt
from auth import SECRET_KEY, ALGORITHM
from schemas import UserCreate, UserResponse, Token, UserLogin, URLUpdate
from crud import create_user, get_user_by_email, get_user_urls

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://ml_service:8000")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="URL Shortener API", lifespan=lifespan)


# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
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

# ---------------- AUTH DEPENDENCY ----------------
async def get_current_user_optional(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    user = await get_user_by_email(db, email=email)
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ---------------- ENDPOINTS ----------------

@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await create_user(db, user)

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/urls", response_model=list[URLResponse])
async def read_user_urls(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_user_urls(db, user_id=current_user.id)

@app.post("/shorten", response_model=URLResponse)
async def shorten_url(
    url: URLCreate,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
    current_user = Depends(get_current_user_optional)
):
    await check_safe_url(str(url.original_url))

    user_id = current_user.id if current_user else None
    db_url = await create_url(db, url, user_id=user_id)

    # Cache it (fail silently if Redis is down)
    try:
        await redis_client.set(f"url:{db_url.short_id}",
                               str(db_url.original_url),
                               ex=86400)
    except Exception as e:
        print(f"[Cache] Redis error: {e}")
    
    return db_url


@app.put("/urls/{short_id}", response_model=URLResponse)
async def update_url_endpoint(
    short_id: str,
    url_update: URLUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_url = await get_url_by_short_id(db, short_id)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    if db_url.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this URL")
    
    return await update_url(db, db_url, url_update)


@app.delete("/urls/{short_id}")
async def delete_url_endpoint(
    short_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_url = await get_url_by_short_id(db, short_id)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    if db_url.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this URL")
    
    await delete_url(db, db_url)
    return {"message": "URL deleted successfully"}


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

    # Parse User Agent
    ua_string = request.headers.get("User-Agent", "")
    user_agent = parse(ua_string)
    browser = user_agent.browser.family
    os_name = user_agent.os.family
    device = user_agent.device.family

    # Get Country (Async)
    # We can do this inside the background task function to avoid blocking response
    # But background_tasks.add_task expects a function.
    # Let's create a wrapper function.
    
    background_tasks.add_task(
        record_stats,
        db,
        short_id,
        request.client.host,
        ua_string,
        request.headers.get("Referer")
    )

    return RedirectResponse(url=original_url)

async def record_stats(db: AsyncSession, short_id: str, ip: str, ua_string: str, referrer: str):
    user_agent = parse(ua_string)
    browser = user_agent.browser.family
    os_name = user_agent.os.family
    device = user_agent.device.family
    
    country = "Unknown"
    if ip and ip != "127.0.0.1" and ip != "::1":
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://ip-api.com/json/{ip}", timeout=2) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("status") == "success":
                            country = data.get("country", "Unknown")
        except Exception as e:
            print(f"[Stats] Geo error: {e}")

    await create_url_stats(
        db,
        short_id,
        ip=ip,
        country=country,
        browser=browser,
        os=os_name,
        device=device,
        referrer=referrer
    )


@app.get("/stats/{short_id}", response_model=URLStatsResponse)
async def get_stats(short_id: str, db: AsyncSession = Depends(get_db)):
    stats = await get_url_stats(db, short_id)
    return stats


@app.get("/qr/{short_id}")
async def get_qr_code(short_id: str, request: Request):
    # Construct the full URL
    # Use request.base_url to get the current scheme/host/port
    # Or hardcode if behind proxy, but dynamic is better for portability
    full_url = str(request.base_url).rstrip('/') + f"/{short_id}"
    
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(full_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return StreamingResponse(img_byte_arr, media_type="image/png")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
