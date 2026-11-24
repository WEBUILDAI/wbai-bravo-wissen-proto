PYTHON ?= python3

.PHONY: help install compile lint format test validate verify abgelaufen

help: ## Ziele anzeigen
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "%-12s %s\n", $$1, $$2}'

install: ## Abhängigkeiten installieren (gepinnt)
	$(PYTHON) -m pip install -r requirements.txt

compile: ## requirements.in -> requirements.txt pinnen
	$(PYTHON) -m piptools compile --strip-extras --quiet -o requirements.txt requirements.in

lint: ## Ruff + Black (nur prüfen)
	$(PYTHON) -m ruff check scripts tests
	$(PYTHON) -m black --check scripts tests

format: ## Ruff-Fixes + Black anwenden
	$(PYTHON) -m black scripts tests
	$(PYTHON) -m ruff check --fix scripts tests

test: ## Pytest
	$(PYTHON) -m pytest -q

validate: ## Einträge gegen das Schema prüfen
	$(PYTHON) scripts/validate.py

abgelaufen: ## Abgelaufene Einträge auflisten
	$(PYTHON) scripts/validate.py --abgelaufen

verify: lint test validate ## Gate für lokal, Hooks und CI
