from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ORIGINS
from exchange_rates import router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
