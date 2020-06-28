format:
	poetry run black typegripe tests

check-format:
	poetry run black --check typegripe tests

check-type:
	poetry run mypy typegripe tests

test:
	poetry run pytest tests

ci-check: check-format check-type test
