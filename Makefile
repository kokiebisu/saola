OPTIONS ?=
SCRIPT_PREFIX = docker compose exec script python

start-container:
	docker compose up -d

recreate-container:
	docker compose up --build --remove-orphans -d

stop-container:
	docker compose down

saola:
	$(SCRIPT_PREFIX) /app/saola.py $(OPTIONS)

scrape:
	$(SCRIPT_PREFIX) /app/scrape.py $(OPTIONS)

compile:
	$(SCRIPT_PREFIX) /app/compile.py $(OPTIONS)
