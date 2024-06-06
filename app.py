from flask import Flask

from log import Logger

log = Logger.get_instance()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

