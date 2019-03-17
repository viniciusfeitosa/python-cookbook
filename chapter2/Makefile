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

up:
		# docker stop $(shell docker ps -aq)
		docker-compose -f docker-compose.yml up --build -d
		sleep 5
		docker-compose ps

flask-initmigration:
		docker-compose exec news_flask flask db init

flask-makemigrate:
		docker-compose exec news_flask flask db migrate

flask-migrate:
		docker-compose exec news_flask flask db upgrade

nameko-initmigration:
		docker-compose exec news_nameko alembic revision --autogenerate -m "baseline"

nameko-migrate:
		docker-compose exec news_nameko alembic upgrade head