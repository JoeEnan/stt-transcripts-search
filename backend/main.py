from contextlib import asynccontextmanager

from database import init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import health, transcriptions, websocket

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Ensuring database exists")
    init_db()

    yield
    print("Cleaning up models")


app.router.lifespan_context = lifespan

app.include_router(health.router)
app.include_router(transcriptions.router)
app.include_router(websocket.router)

AUDIO_STORAGE_PATH = "audio_storage"
app.mount("/audio_storage", StaticFiles(directory=AUDIO_STORAGE_PATH))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=9090, reload=True)
