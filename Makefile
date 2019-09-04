DOCKER_COMPOSE_FILE=docker-compose.yaml
DOCKER_COMPOSE=docker-compose -f ${DOCKER_COMPOSE_FILE}

start_dev_env:
	${DOCKER_COMPOSE} \
		up -d \
		iosxe \
		nxos \
		junos

stop_dev_env:
	${DOCKER_COMPOSE} \
		down

test_unit:
	python -m pytest \
	--cov=ssh2net \
	--cov-report html \
	--cov-report term \
	tests/unit/.

test_functional:
	python -m pytest \
	--cov=ssh2net \
	--cov-report html \
	--cov-report term \
	tests/functional/. \
	--ignore tests/functional/junos \
	--ignore tests/functional/eos \
	--ignore tests/functional/comparison_tests

test_all:
	python -m pytest \
	--cov=ssh2net \
	--cov-report html \
	--cov-report term \
	tests/. \
	--ignore tests/functional/junos \
	--ignore tests/functional/eos \
	--ignore tests/functional/comparison_tests

test_iosxe:
	python -m pytest \
	--cov=ssh2net \
	--cov-report html \
	--cov-report term \
	tests/. \
	--ignore tests/functional/nxos \
	--ignore tests/functional/junos \
	--ignore tests/functional/eos \
	--ignore tests/functional/comparison_tests

test_nxos:
	python -m pytest \
	--cov=ssh2net \
	--cov-report html \
	--cov-report term \
	tests/. \
	--ignore tests/functional/iosxe \
	--ignore tests/functional/junos \
	--ignore tests/functional/eos \
	--ignore tests/functional/comparison_tests

.PHONY: docs
docs:
	python -m pdoc \
	--html \
	--output-dir docs \
	ssh2net \
	--force
