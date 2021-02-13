-include .env

SHELL := /bin/bash

all:
	@echo "make devenv		- Create & setup development virtual environment"
	@echo "make postgres    - Start postgres container (need to specify .env file)"
	@echo "make clean		- Remove files created by distutils"
	@exit 0

clean:
	rm -fr *.egg-info dist

devenv: clean
	rm -rf env
	python3.8 -m venv env
	env/bin/pip install -Ue '.[dev]'

postgres:
	docker stop tracker-postgres || true
	docker run --rm --detach --name=tracker-postgres \
		--env POSTGRES_USER=${postgres_user} \
		--env POSTGRES_PASSWORD=${postgres_password} \
		--env POSTGRES_DB=${postgres_database} \
		--publish ${postgres_port}:5432 postgres:12