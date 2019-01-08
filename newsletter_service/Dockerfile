FROM python:alpine3.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install pipenv

RUN pipenv install --system --skip-lock

CMD ["python", "/app/newspaper/manage.py", "runserver", "0.0.0.0:8080"]
