from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.core.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.game.router import router as game_router


Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [settings.FRONTEND_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(game_router)
