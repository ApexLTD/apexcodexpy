install:
	python -m pip install --upgrade pip poetry
	poetry install

test:
	poetry run pytest tests --cov --last-failed
