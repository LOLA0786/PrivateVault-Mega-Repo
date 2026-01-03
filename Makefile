.PHONY: install test lint format clean docker-build docker-up

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest

lint:
	black --check src/ tests/
	isort --check-only src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

run-fintech:
	python examples/fintech_demo.py

run-medtech:
	python examples/medtech_demo.py
