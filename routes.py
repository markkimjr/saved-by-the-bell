import traceback
from flask import Response

from app import app
from log import Logger

log = Logger.get_instance()


@app.route("/", methods=["GET"])
def render_index() -> Response:
    try:
        return "Saved by the bell"
    except Exception as e:
        traceback.print_exc()
        log.error(f"ERROR OCCURRED WHILE RENDERING INDEX")

