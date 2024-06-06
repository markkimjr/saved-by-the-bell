import traceback
from flask import Flask, Response

from log import Logger

log = Logger.get_instance()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route("/", methods=["GET"])
def render_index() -> Response:
    try:
        return "Saved by the bell"
    except Exception as e:
        traceback.print_exc()
        log.error(f"ERROR OCCURRED WHILE RENDERING INDEX")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

