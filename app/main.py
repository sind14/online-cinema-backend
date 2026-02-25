from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.seed import seed_user_groups
from app.auth.router import router as auth_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_user_groups()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])


@app.get("/")
def root():
    return {"message": "Online Cinema API is running"}
