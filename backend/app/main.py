import logging
from fastapi import Request
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from app.config import settings
from app.db.session import init_db
from app.routers import auth, movies, watchlist, chat

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not (settings.skip_db_init or getattr(app.state, "skip_db_init", False)):
        await init_db()
    yield

app = FastAPI(
    title = "Cine API Advisor",
    description = "AI-powered movie and TV watchlist platform",
    version="0.1.0",
    lifespan=lifespan
)

app.state.skip_db_init = settings.skip_db_init

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(watchlist.router)
app.include_router(chat.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "message": "Request validation failed"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "message": "Cine AI Advisor is running"
    }
