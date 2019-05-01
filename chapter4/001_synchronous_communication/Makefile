.PHONY: help

stop:
		docker stop $(shell docker ps -aq)

clean:
		docker stop $(shell docker ps -aq)
		docker rm $(shell docker ps -aq)

destroy:
		docker stop $(shell docker ps -aq)
		docker rm $(shell docker ps -aq)
		docker rmi -f $(shell docker images -q)

up:
		# docker stop $(shell docker ps -aq)
		docker-compose -f docker-compose.yml up --build -d
		sleep 5
		docker-compose -f docker-compose.yml ps

initmigration:
		docker-compose -f docker-compose.yml exec orders_service alembic revision --autogenerate -m "baseline"

migrate:
		docker-compose -f docker-compose.yml exec orders_service alembic upgrade head

status:
		docker-compose -f docker-compose.yml ps
