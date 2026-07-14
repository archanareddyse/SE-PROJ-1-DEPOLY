"""
Thin data-access layer around MongoDB Atlas using PyMongo.

We use a single lazily-created MongoClient and reuse it for the life of
the process (PyMongo's client is already connection-pooled internally,
so there's no need to open/close a connection per-request).
"""

from django.conf import settings
from pymongo import MongoClient
from pymongo.server_api import ServerApi

_client = None


def get_client():
    global _client
    if _client is None:
        if not settings.MONGO_URI:
            raise RuntimeError(
                "MONGO_URI is not set. Copy backend/.env.example to backend/.env "
                "and fill in your MongoDB Atlas connection string."
            )
        _client = MongoClient(settings.MONGO_URI, server_api=ServerApi("1"))
    return _client


def get_db():
    return get_client()[settings.MONGO_DB_NAME]


def get_tasks_collection():
    return get_db()["tasks"]
