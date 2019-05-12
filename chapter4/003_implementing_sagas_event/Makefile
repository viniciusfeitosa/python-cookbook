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

build-up:
		# docker stop $(shell docker ps -aq)
		docker-compose -f docker-compose.yml up --build -d
		sleep 5
		docker-compose -f docker-compose.yml ps

up:
		docker stop $(shell docker ps -aq)
		docker-compose -f docker-compose.yml up -d
		sleep 5
		docker-compose -f docker-compose.yml ps

initmigration_orders:
		docker-compose -f docker-compose.yml exec orders_service alembic revision --autogenerate -m "baseline"

migrate_orders:
		docker-compose -f docker-compose.yml exec orders_service alembic upgrade head

initmigration_payments:
		docker-compose -f docker-compose.yml exec payment_service alembic revision --autogenerate -m "baseline"

migrate_payments:
		docker-compose -f docker-compose.yml exec payment_service alembic upgrade head

initmigration_inventory:
		docker-compose -f docker-compose.yml exec inventory_service alembic revision --autogenerate -m "baseline"

migrate_inventory:
		docker-compose -f docker-compose.yml exec inventory_service alembic upgrade head

initmigration:	initmigration_orders initmigration_payments	initmigration_inventory

migrate: migrate_orders	migrate_payments migrate_inventory

status:
		docker-compose -f docker-compose.yml ps
