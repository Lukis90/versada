from typing import Optional

from bson.objectid import ObjectId
from pymongo import cursor, database

from db import Collections


def insert_transaction(client: database, transaction: dict) -> ObjectId:
    res = client[Collections.TRANSACTIONS].insert_one(transaction)
    return res.inserted_id


def get_transactions(
    client: database, filter: dict, projection: Optional[dict] = None
) -> cursor:
    return client[Collections.TRANSACTIONS].find(
        filter=filter,
        projection=projection,
    )
