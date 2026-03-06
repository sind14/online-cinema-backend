from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.seed import seed_user_groups
from app.auth.router import router as auth_router
from app.routers.genre import router as genre_router
from app.routers.movie import router as movie_router
from app.routers.director import router as director_router
from app.routers.star import router as star_router
from app.routers.certification import router as certification_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_user_groups()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(genre_router, prefix="/genres", tags=["Genres"])
app.include_router(director_router, prefix="/directors", tags=["Directors"])
app.include_router(star_router, prefix="/stars", tags=["Stars"])
app.include_router(certification_router, prefix="/certifications", tags=["Certifications"])
app.include_router(movie_router, prefix="/movies", tags=["Movies"])


@app.get("/")
def root():
    return {"message": "Online Cinema API is running"}
