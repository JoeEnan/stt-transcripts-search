from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from database import init_db
from log_config import logger
from routes import health, transcriptions, websocket
from utils.websocket_manager import clear_websockets

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001, `app` is required for lifespan context manager
    logger.info("Ensuring database exists")
    init_db()

    yield
    # This will clear all connected websockets when lifecycle ends
    clear_websockets()


app.router.lifespan_context = lifespan

app.include_router(health.router)
app.include_router(transcriptions.router)
app.include_router(websocket.router)

app.mount("/api/audio_storage", StaticFiles(directory=settings.AUDIO_STORAGE_PATH))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=9090, reload=False)
