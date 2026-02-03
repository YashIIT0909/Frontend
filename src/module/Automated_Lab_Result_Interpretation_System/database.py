import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

load_dotenv()

MONGODB_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "result_interpretation_engine")

if not MONGODB_URI:
    raise RuntimeError(
        "MongoDB URI not found. Set MONGO_URI or MONGODB_URI in .env or environment."
    )

_client: MongoClient | None = None
_database: Database | None = None


def connect_to_mongo() -> None:
    global _client, _database
    if _client is not None:
        return

    _client = MongoClient(MONGODB_URI)
    _client.admin.command("ping")
    _database = _client[MONGODB_DB_NAME]


def close_mongo() -> None:
    global _client, _database
    if _client is not None:
        _client.close()
    _client = None
    _database = None


def get_database() -> Database:
    if _database is None:
        raise RuntimeError("MongoDB is not connected. Call connect_to_mongo() first.")
    return _database


def get_collection(name: str) -> Collection:
    return get_database()[name]


def get_lab_results_collection() -> Collection:
    return get_collection("lab_results")
