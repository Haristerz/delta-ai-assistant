from fastapi import FastAPI
from contextlib import asynccontextmanager

from backend.database import init_db
from backend.routers import auth, miles, activity, profile, invoice, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Delta Air Lines AI Assistant",
    description="Customer assistant API with JWT auth and AI chat",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router,     prefix="/auth",     tags=["Auth"])
app.include_router(miles.router,    prefix="/miles",    tags=["Miles"])
app.include_router(activity.router, prefix="/activity", tags=["Activity"])
app.include_router(profile.router,  prefix="/profile",  tags=["Profile"])
app.include_router(invoice.router,  prefix="/invoice",  tags=["Invoice"])
app.include_router(chat.router,     prefix="/chat",     tags=["Chat"])


@app.get("/")
def root():
    return {"message": "Delta AI Assistant is running"}
