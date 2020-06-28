format:
	poetry run black typegripe tests

check-format:
	poetry run black --check typegripe tests

check-type:
	poetry run mypy typegripe tests

test:
	poetry run pytest tests

bandit:
	poetry run bandit -r typegripe

flake8:
	poetry run flake8 --max-complexity 10 typegripe tests

pylint:
	poetry run pylint typegripe tests

lint: flake8 pylint

ci-check: check-format check-type lint bandit test
