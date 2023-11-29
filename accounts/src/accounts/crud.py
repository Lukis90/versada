from typing import Optional

from bson.objectid import ObjectId
from pymongo import cursor, database

from db import Collections
from schemas import OID


def create_account(client: database, account: dict) -> OID:
    accounts_coll = client[Collections.ACCOUNTS]
    res = accounts_coll.insert_one(account)
    return res.inserted_id


def get_accounts(client: database, filter: dict, projection: dict) -> cursor:
    accounts_coll = client[Collections.ACCOUNTS]
    return accounts_coll.find(filter, projection)


def get_account(
    client: database, filter: dict, projection: Optional[dict] = None
) -> Optional[dict]:
    return client[Collections.ACCOUNTS].find_one(filter=filter, projection=projection)


def update_balance(client: database, account_id: OID, balance: float):
    balance = round(balance, 2)
    account_coll = client[Collections.ACCOUNTS]
    account_coll.update_one(
        {"_id": ObjectId(account_id)}, {"$set": {"balance": balance}}
    )
