.PHONY: help clean dev doc format install test release

help:
	@echo "Please use \`make <target>\` where <target> is one of"
	@echo "  clean      to clean the repository"
	@echo "  doc        to make the documentation (html)"
	@echo "  dev        to install everything needed to contribute to the project"
	@echo "  format     to correct code style"
	@echo "  install    to install the dependencies required to run the tests"
	@echo "  test       to test peony"

clean:
	@rm -rf build dist .cache .coverage* .tox
	@rm -rf *.egg-info
	@python3 setup.py clean --all > /dev/null 2> /dev/null

doc:
	sphinx-build -b html -d build/doctrees docs build/html
	@printf "\nBuild finished. The HTML pages are in build/html.\n"

dev:
	pip3 install --upgrade pip wheel
	pip3 install --upgrade -r dev_requirements.txt

format:
	@isort -rc examples peony tests > /dev/null
	@autopep8 -r --in-place examples peony tests
	@autoflake -r --in-place examples peony tests

install:
	pip3 install --upgrade pip wheel
	pip3 install --upgrade -r requirements.txt
	pip3 install --upgrade -r extras_require.txt

test:
	flake8
	py.test --cov=peony --cov-report term-missing --durations=20 tests

release:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*
