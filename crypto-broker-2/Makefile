dev:
	docker compose up --build

down:
	docker compose down

clean:
	docker compose down -v

test:
	docker compose run --rm api pytest

logs:
	docker compose logs -f

migration:
	docker compose run --rm api alembic revision --autogenerate -m "$(m)"

upgrade:
	docker compose run --rm api alembic upgrade head
