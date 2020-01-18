DOCKER_COMPOSE_FILE=docker-compose.yaml
DOCKER_COMPOSE=docker-compose -f ${DOCKER_COMPOSE_FILE}

start_dev_env:
	${DOCKER_COMPOSE} \
		up -d \
		iosxe \
		nxos \
		junos \
		iosxr

start_dev_env_iosxe:
	${DOCKER_COMPOSE} \
		up -d \
		iosxe

start_dev_env_nxos:
	${DOCKER_COMPOSE} \
		up -d \
		nxos

start_dev_env_iosxr:
	${DOCKER_COMPOSE} \
		up -d \
		iosxr

start_dev_env_junos:
	${DOCKER_COMPOSE} \
		up -d \
		junos

start_dev_env_eos:
	${DOCKER_COMPOSE} \
		up -d \
		eos

stop_dev_env:
	${DOCKER_COMPOSE} \
		down

# run with sudo!
add_delay_dev_env:
	tc qdisc del dev br_ssh2net root; \
	tc qdisc add dev br_ssh2net root handle 1: prio; \
	tc qdisc add dev br_ssh2net parent 1:3 handle 30: tbf rate 20kbit buffer 1600 limit 3000; \
	tc qdisc add dev br_ssh2net parent 30:1 handle 31: netem  delay 1000ms 10ms distribution normal loss 10%; \
	tc filter add dev br_ssh2net protocol ip parent 1:0 prio 3 u32 match ip dst 172.18.0.0/26 flowid 1:3

# run with sudo!
remove_delay_dev_env:
	tc qdisc del dev br_ssh2net root

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
	--ignore tests/functional/comparison_tests

test_all:
	python -m pytest \
	--cov=ssh2net \
	--cov-report html \
	--cov-report term \
	tests/.

test_iosxe:
	python -m pytest \
	--cov=ssh2net \
	--cov-report html \
	--cov-report term \
	tests/unit \
	tests/functional/cisco_iosxe

test_nxos:
	python -m pytest \
	--cov=ssh2net \
	--cov-report html \
	--cov-report term \
	tests/unit \
	tests/functional/cisco_nxos

test_iosxr:
	python -m pytest \
	--cov=ssh2net \
	--cov-report html \
	--cov-report term \
	tests/unit \
	tests/functional/cisco_iosxr

test_junos:
	python -m pytest \
	--cov=ssh2net \
	--cov-report html \
	--cov-report term \
	tests/unit \
	tests/functional/juniper_junos

test_eos:
	python -m pytest \
	--cov=ssh2net \
	--cov-report html \
	--cov-report term \
	tests/unit \
	tests/functional/arista_eos

.PHONY: docs
docs:
	python -m pdoc \
	--html \
	--output-dir docs \
	ssh2net \
	--force
