import traceback
from typing import List, Union
from functools import wraps
from google.cloud import firestore

from settings import PROJECT_ID
from log import Logger

log = Logger.get_instance()

db = None


def init_db() -> None:
    global db
    if db is None:
        db = firestore.Client(PROJECT_ID)


def db_transaction(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        init_db()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            log.error(f"ERROR OCCURRED WHILE CONNECTING TO DB: {e}")
        finally:
            if db:
                db.close()
    return wrapper


@db_transaction
def bulk_insert(collection: str, data: List[Union[dict, object]]) -> None:
    batch = db.batch()
    for doc in data:
        doc_ref = db.collection(collection).document()
        if isinstance(doc, dict):
            batch.set(doc_ref, doc)
        if isinstance(doc, object):
            batch.set(doc_ref, doc.__dict__)
    batch.commit()


@db_transaction
def bulk_select(collection: str) -> List[dict]:
    docs = db.collection(collection).stream()
    return [doc.to_dict() for doc in docs]
