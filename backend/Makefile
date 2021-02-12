-include .env

SHELL := /bin/bash

all:
	@echo "make devenv		- Create & setup development virtual environment"
	@echo "make clean		- Remove files created by distutils"
	@exit 0

clean:
	rm -fr *.egg-info dist

devenv: clean
	rm -rf env
	python3.8 -m venv env
	env/bin/pip install -Ue '.[dev]'

