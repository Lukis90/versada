from enum import StrEnum

from pymongo import MongoClient

from config import MONGO_CONN


class Collections(StrEnum):
    ACCOUNTS = "accounts"
    TRANSACTIONS = "transactions"


def get_client() -> MongoClient:
    client = MongoClient(MONGO_CONN)
    try:
        yield client["bank"]
    finally:
        client.close()
