from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import init_db
from app.routers import auth, movies, watchlist

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title = "Cine API Advisor",
    description = "AI-powered movie and TV watchlist platform",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(watchlist.router)


@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "message": "Cine AI Advisor is running"
    }