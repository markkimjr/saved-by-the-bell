FROM python:3.10

COPY requirements.txt ./

RUN set -ex; \
    pip install -r requirements.txt; \
    pip install gunicorn

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

CMD exec gunicorn --bind :$PORT --timeout 600 --workers 1 --threads 4 app:app