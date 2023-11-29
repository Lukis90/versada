from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from accounts.controller import router as accounts_rounter
from config import ORIGINS
from transactions.controller import router as transaction_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(accounts_rounter)
app.include_router(transaction_router)


@app.get("/")
async def root():
    return {"message": "Versada Bank"}
