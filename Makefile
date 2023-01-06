app: environment
	rm Makefile poetry.lock poetry.toml

build:
	"tools/releasing/build.sh"

coverage:
	poetry run tools/qa/coverage/update.sh

environment: poetry.lock
	command -v poetry || pip install --user poetry
	poetry install

format:
	poetry run tools/qa/format.sh

run:
	"src/bin/run.sh"

test: test_src test_qa

test_src:
	poetry run pytest --cov=src --numprocesses=auto "tests/src"
	poetry run python --version | cut -d. -f1,2 > "tools/qa/coverage/report.txt"
	poetry run coverage report >> "tools/qa/coverage/report.txt"
	poetry run coverage html --directory "tools/qa/coverage/html"

test_qa:
	poetry run pytest --numprocesses=auto "tests/qa"

upload:
	"tools/releasing/upload.sh"

vscode: environment
	make test_src || true


.PHONY: help
help:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
