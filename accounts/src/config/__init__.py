import os

ORIGINS = ["*"]
MONGO_CONN = os.getenv("MONGO_CONN", "mongodb://localhost:27017")
EXCHANGE_URL = os.getenv("EXCHANGE_URL", "http://localhost:8001/exchange/rates/{pair}")
