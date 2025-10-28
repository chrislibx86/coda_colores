from pymongo import MongoClient
from db.config import MONGO_CODA_URI, SERVER_API


def get_cliente():
    try:
        cliente = MongoClient(MONGO_CODA_URI, server_api=SERVER_API)
        return cliente
    except Exception as e:
        return None