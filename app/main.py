# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from app.routers import booking
from app.database import Base, engine
from app.config import settings
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("starting up..")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the database tables if they do not exist
Base.metadata.create_all(bind=engine)

app.include_router(booking.router, prefix="/api/v1", tags=["api"])
#app.include_router(auth.router, tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the API of " + settings.app_name + ". If you want to play around with the API go to: ./docs"}

#app.mount("/static", StaticFiles(directory="app/static"), name="static")

# You can also mount your templates directory if you are using Jinja2 templates
# from fastapi.templating import Jinja2Templates
# templates = Jinja2Templates(directory="app/templates")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
