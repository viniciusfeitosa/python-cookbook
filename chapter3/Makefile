.PHONY: help

status:
		docker-compose ps

stop:
		docker stop $(shell docker ps -aq)

clean:
		docker stop $(shell docker ps -aq)
		docker rm $(shell docker ps -aq)

destroy:
		docker stop $(shell docker ps -aq)
		docker rm $(shell docker ps -aq)
		docker rmi -f $(shell docker images -q)

# ----------------------------------------
# ----------------------------------------
# News Service CQRS
# ----------------------------------------
# ----------------------------------------
up_cqrs:
		# docker stop $(shell docker ps -aq)
		docker-compose -f docker-compose_cqrs.yml up --build -d
		sleep 5
		docker-compose ps

initmigration_cqrs:
		docker-compose exec news_nameko_cqrs alembic revision --autogenerate -m "baseline"

migrate_cqrs:
		docker-compose exec news_nameko_cqrs alembic upgrade head

# ----------------------------------------
# ----------------------------------------
# News Service Event Sourcing
# ----------------------------------------
# ----------------------------------------
up_es:
		# docker stop $(shell docker ps -aq)
		docker-compose -f docker-compose_es.yml up --build -d
		sleep 5
		docker-compose ps

initmigration_es:
		docker-compose exec news_nameko_es alembic revision --autogenerate -m "baseline"

migrate_es:
		docker-compose exec news_nameko_es alembic upgrade head