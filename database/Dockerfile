FROM debezium/postgres:9.6

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# run create.sql on init
COPY create.sql /docker-entrypoint-initdb.d/
