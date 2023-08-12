FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y gcc python3-dev musl-dev libmagic1 libffi-dev netcat-traditional \
    build-essential libpq-dev cron vim

COPY poetry.lock pyproject.toml /app/

RUN pip3 install poetry

RUN poetry install

COPY . /app/

# Cron Job
COPY crontab /etc/cron.d/crontab

RUN chmod 0644 /etc/cron.d/crontab

RUN touch /var/log/cron.log

RUN crontab /etc/cron.d/crontab

RUN chmod +x ./entrypoint.sh

ENV PYTHONPATH "${PYTHONPATH}:/usr/local/lib/python3.10/site-packages"

ENTRYPOINT [ "./entrypoint.sh" ]
