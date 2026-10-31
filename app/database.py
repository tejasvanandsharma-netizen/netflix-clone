from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
# Render के लिए /tmp फोल्डर का इस्तेमाल करें, वहाँ लिखने की परमिशन होती है
SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/movies.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# यह फंक्शन डेटाबेस सेशन देने का काम करता है
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()