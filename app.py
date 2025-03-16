from sqlalchemy import create_engine , Column , Integer , String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker , Session
import sqlite3


from fastapi import FastAPI , Depends
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

app = FastAPI()


DATABASE_URL= "sqlite:///./test.db"

engine = create_engine(DATABASE_URL , connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False , autoflush=False , bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer , primary_key=True , index=True)
    name = Column(String , index=True)
    email = Column(String , index=True , unique=True)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users" , response_model=UserCreate)
def create_user(user: UserCreate , db: Session = Depends(get_db)):
    db_user = User(name=user.name , email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


class UserResponse(BaseModel):
    name: str
    email: str


@app.get("/users/" , response_model=list[UserResponse])
def getUsers(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


