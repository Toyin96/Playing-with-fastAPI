from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Boolean, Column, String, Float, Integer
from sqlalchemy.orm import declarative_base, Session, sessionmaker

app = FastAPI()

# SQLALCHEMY SETUP
SQLALCHEMY_DATABASE_URL = "postgresql://magna:m18job,,@localhost/placesdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DBPLace(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    coffee = Column(Boolean)
    wifi = Column(Boolean)
    food = Column(Boolean)
    lat = Column(Float)
    lng = Column(Float)


class Place(BaseModel):
    name: str
    description: Optional[str] = None
    coffee: bool
    wifi: bool
    food: bool
    lat: float
    lng: float

    class Config:
        orm_mode = True


def get_place(db: Session, place_id: int):
    return db.query(DBPLace).where(DBPLace.id == place_id).first()


def get_places(db: Session):
    return db.query(DBPLace).all()


def create_place(db: Session, place: Place):
    place_obj = DBPLace(**place.dict())
    db.add(place_obj)
    db.commit()
    db.refresh(place_obj)
    return place_obj


Base.metadata.create_all(bind=engine)


# the views
@app.get("/")
def index():
    return {"message": "hello world"}


@app.get("/place/{place_id}")
def get_place_view(place_id: int, db: Session = Depends(get_db)):
    return get_place(db, place_id=place_id)


@app.get("/places/", response_model=List[Place])
def get_places_view(db: Session = Depends(get_db)):
    return get_places(db=db)


@app.post("/places/", response_model=Place)
def create_place_view(place: Place, db: Session = Depends(get_db)):
    return create_place(db=db, place=place)
