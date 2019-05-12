FROM postgres

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# run create.sql on init
COPY create.sql /docker-entrypoint-initdb.d/
