FROM python:3.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app

RUN pip install pipenv

RUN pipenv install --skip-lock --system --deploy

CMD ["uwsgi", "--ini", "uwsgi.ini"]