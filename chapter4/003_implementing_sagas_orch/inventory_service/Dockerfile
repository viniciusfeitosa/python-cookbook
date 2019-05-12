FROM python:3.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app

RUN pip install pipenv

RUN pipenv install --skip-lock --system --deploy

ENTRYPOINT ["nameko"]

CMD ["run", "--config",  "config.yaml", "src.app"]

EXPOSE 5000
