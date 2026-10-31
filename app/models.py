from sqlalchemy import Column, Integer, String, Float, Text
from .database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True) # यह होना जरूरी है
    title = Column(String, index=True)
    overview = Column(Text)
    poster_path = Column(String)
    backdrop_path = Column(String)
    vote_average = Column(Float)
    release_date = Column(String)