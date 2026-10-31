"""FastAPI entry point for the movie catalog starter project."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .database import Base, engine, get_db
# यहाँ हमने fetch_movies_by_language भी इम्पोर्ट कर लिया है
from .movie_api import fetch_popular_movies, fetch_movie_trailer, fetch_movies_by_language
from .schemas import MovieOut, SyncResult

BASE_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the SQLite database and tables the first time the app starts.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="StreamFlix Movie Catalog", version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/movies", response_model=list[MovieOut])
def list_movies(db: Session = Depends(get_db)):
    return db.scalars(select(models.Movie).order_by(models.Movie.vote_average.desc())).all()


@app.post("/api/movies/sync", response_model=SyncResult)
async def sync_movies(db: Session = Depends(get_db)):
    """Import/update popular movie metadata from TMDB into the local database."""
    try:
        # यहाँ हमने fetch_popular_movies की जगह fetch_movies_by_language लगा दिया है
        remote_movies = await fetch_movies_by_language()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not fetch movies from TMDB. Check the API key and internet connection.",
        ) from exc

    for data in remote_movies:
        movie = db.query(models.Movie).filter(models.Movie.tmdb_id == data["tmdb_id"]).first()
        if movie is None:
            movie = models.Movie(**data)
            db.add(movie)
        else:
            for key, value in data.items():
                setattr(movie, key, value)

    db.commit()
    return SyncResult(imported=len(remote_movies), message="Movie metadata synced successfully.")


@app.get("/health")
def health_check():
    return {"status": "ok"}