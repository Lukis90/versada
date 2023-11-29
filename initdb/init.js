db = db.getSiblingDB('bank');
db.createCollection('transactions');
db.transactions.ensureIndex({'date': 1});
db.transactions.ensureIndex({'account_id': 1});
