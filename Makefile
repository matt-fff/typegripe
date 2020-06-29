build:
	poetry build

format:
	poetry run black typegripe tests

check-format:
	poetry run black --check .

check-type:
	poetry run mypy typegripe tests

test:
	poetry run pytest -n auto tests

test-cov:
	poetry run pytest -n auto --cov=typegripe tests

bandit:
	poetry run bandit -r typegripe

flake8:
	poetry run flake8 --max-complexity 10 .

pylint:
	poetry run pylint typegripe tests

lint: flake8 pylint

ci-check: check-format check-type lint bandit test-cov
