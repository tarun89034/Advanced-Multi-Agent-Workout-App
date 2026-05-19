from dotenv import load_dotenv
import streamlit as st
import os
import uuid
from loguru import logger

load_dotenv()

ENDPOINT = os.getenv("ASTRA_ENDPOINT")
TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")


class _InsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class _InMemoryCollection:
    """Thread-safe in-memory fallback when AstraDB is unavailable."""

    def __init__(self):
        self._items = []

    def insert_one(self, doc):
        new_doc = dict(doc)
        new_doc.setdefault("_id", str(uuid.uuid4()))
        self._items.append(new_doc)
        return _InsertResult(new_doc["_id"])

    def find_one(self, query):
        target = query.get("_id", {}).get("$eq")
        for item in self._items:
            if item.get("_id") == target:
                return dict(item)
        return None

    def find(self, query):
        target = query.get("user_id", {}).get("$eq")
        return [dict(item) for item in self._items if item.get("user_id") == target]

    def update_one(self, query, update):
        target = query.get("_id")
        set_values = update.get("$set", {})
        for item in self._items:
            if item.get("_id") == target:
                item.update(set_values)
                break

    def delete_one(self, query):
        target = query.get("_id")
        self._items = [item for item in self._items if item.get("_id") != target]


class _SafeCollectionProxy:
    """Wraps a real AstraDB collection and falls back to in-memory on any error."""

    def __init__(self, real_collection, fallback: _InMemoryCollection):
        self._real = real_collection
        self._fallback = fallback
        self._use_fallback = False

    def _switch_to_fallback(self, method_name, exc):
        logger.warning(
            f"AstraDB {method_name} failed ({exc}). Switching to in-memory fallback."
        )
        self._use_fallback = True

    def insert_one(self, doc):
        if self._use_fallback:
            return self._fallback.insert_one(doc)
        try:
            return self._real.insert_one(doc)
        except Exception as e:
            self._switch_to_fallback("insert_one", e)
            return self._fallback.insert_one(doc)

    def find_one(self, query):
        if self._use_fallback:
            return self._fallback.find_one(query)
        try:
            return self._real.find_one(query)
        except Exception as e:
            self._switch_to_fallback("find_one", e)
            return self._fallback.find_one(query)

    def find(self, query):
        if self._use_fallback:
            return self._fallback.find(query)
        try:
            result = self._real.find(query)
            return list(result)
        except Exception as e:
            self._switch_to_fallback("find", e)
            return self._fallback.find(query)

    def update_one(self, query, update):
        if self._use_fallback:
            return self._fallback.update_one(query, update)
        try:
            return self._real.update_one(query, update)
        except Exception as e:
            self._switch_to_fallback("update_one", e)
            return self._fallback.update_one(query, update)

    def delete_one(self, query):
        if self._use_fallback:
            return self._fallback.delete_one(query)
        try:
            return self._real.delete_one(query)
        except Exception as e:
            self._switch_to_fallback("delete_one", e)
            return self._fallback.delete_one(query)


@st.cache_resource
def get_db():
    if not ENDPOINT or not TOKEN:
        return None

    try:
        from astrapy import DataAPIClient

        client = DataAPIClient(TOKEN)
        return client.get_database_by_api_endpoint(ENDPOINT)
    except Exception as e:
        logger.warning(f"Failed to connect to AstraDB: {e}")
        return None


db = None
personal_data_collection = None
notes_collection = None

try:
    db = get_db()
except Exception:
    db = None

if db:
    try:
        try:
            db.create_collection("personal_data")
        except Exception:
            pass

        real_personal = db.get_collection("personal_data")
        real_notes = db.get_collection("notes")

        # Wrap with safe proxies that auto-fallback on errors
        personal_data_collection = _SafeCollectionProxy(
            real_personal, _InMemoryCollection()
        )
        notes_collection = _SafeCollectionProxy(real_notes, _InMemoryCollection())
        logger.info("AstraDB collections initialized (with safe fallback proxies).")
    except Exception as e:
        logger.warning(f"AstraDB collection setup failed: {e}. Using in-memory.")
        personal_data_collection = _InMemoryCollection()
        notes_collection = _InMemoryCollection()
else:
    logger.info("No AstraDB config found. Using in-memory storage.")
    personal_data_collection = _InMemoryCollection()
    notes_collection = _InMemoryCollection()
