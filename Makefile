.PHONY: up down build logs ps backend-shell db-shell redis-shell

up:
	docker compose up

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

ps:
	docker compose ps

backend-shell:
	docker compose exec backend bash

db-shell:
	docker compose exec postgres psql -U venture_lab -d venture_lab

redis-shell:
	docker compose exec redis redis-cli