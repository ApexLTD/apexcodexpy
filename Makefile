help:
	poetry run codex

amend:
	git commit --amend --no-edit -a

install:
	python -m pip install --upgrade pip poetry
	poetry install

lock:
	poetry lock

update:
	poetry update

format:
	poetry run codex fix

format-unsafe:
	poetry run codex fix --unsafe

lint:
	poetry run codex lint

test:
	poetry run pytest tests --cov --last-failed
