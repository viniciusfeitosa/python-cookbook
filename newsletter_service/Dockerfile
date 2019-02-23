FROM python:3.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app

# RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install pipenv

RUN pipenv install --skip-lock --system --deploy

# CMD ["python", "/app/manage.py", "runserver", "0.0.0.0:8081"]
CMD ["uwsgi", "--ini", "uwsgi.ini"]
