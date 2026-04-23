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

test:
	poetry run pytest tests --cov --last-failed
