[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

ssh2net
=======

Library focusing on connecting to and communicating with network devices via SSH. Built on [ssh2-python](https://github.com/ParallelSSH/ssh2-python) which provides bindings to libssh2.

ssh2net is focused on being lightweight and pluggable so that it *should* be flexible enough to be adapted to handle connecting to, sending commands, and reading output from most network devices.

# Documentation

Documentation is auto-generated [using pdoc3](https://github.com/pdoc3/pdoc). Documentation is linted (see Linting and Testing section) via pydocstyle.

Documentation is hosted via GitHub Pages and can be found [here.](https://carlmontanari.github.io/ssh2net/docs/ssh2net/index.html) You can also view the readme as a webpage [here.](https://carlmontanari.github.io/ssh2net/)

To regenerate documentation locally, use the following make command:

```
make docs
```


# Platforms

In theory ssh2net should be able to connect to lots of different network devices. At the moment the following devices are included in the "functional" tests and should be pretty reliable:

- Cisco IOS-XE (tested on: 16.04.01)
- Cisco NX-OS (tested on: 9.2.4)
- Juniper JunOS (tested on: 17.3R2.10)

I would like to add functional tests for:

- Cisco IOS-XR
- Arista EOS

Any additional platforms would likely not be included in the "core" platform (and therefore functional testing). Additional platforms could be considered, however a pre-requisite for additional platforms would be the capability to create vrnetlab containers for that platform.

As for platforms to *run* ssh2net on -- it has and will be tested on MacOS and Ubuntu regularly and should work on any POSIX system. It has never been tested on Windows, but I don't see any reason it should not work, however I have no plans on supporting Windows as I don't have access or desire to do so.

## Platform Regex

The `comms_prompt_regex` is perhaps the most important argument to getting SSH2Net working.

The "base" pattern is:

`"^[a-z0-9.\-@()/:]{1,20}[#>$]$"`

This pattern works for (tested on show commands only, but shoudl work on config commands for at leaset IOS-XE, and NX-OS) IOS-XE, NX-OS, JunOS, and IOS-XR.

If you do not wish to match cisco "config" level prompts you can use:

`"^[a-z0-9.-@]{1,20}[#>$]$"`

# Installation

To install from this repository:

```
pip install git+https://github.com/carlmontanari/ssh2net
```

To install from source:

```
git clone https://github.com/carlmontanari/ssh2net
cd ssh2net
python setup.py install
```

I've also attempted to add this to PyPI, so you should be able to pip install it "normally":

```
pip install ssh2net
```

# Examples

TODO

# FAQ

TBA, probably things though!

# Linting and Testing

## Linting

This project uses [black](https://github.com/psf/black) for auto-formatting. In addition to black, tox will execute [pylama](https://github.com/klen/pylama), and [pydocstyle](https://github.com/PyCQA/pydocstyle) for linting purposes. I have began playing with adding type hinting and testing this with [mypy](https://github.com/python/mypy), however I've not added this to tox at this point.

## Testing

I broke testing into two main categories -- unit and functional. Unit is what you would expect -- unit testing the code. Functional testing connects to virtual devices in order to more accurately test the code.

### Unit Tests

Unit tests can be executed via pytest or using the following make command:

```
make test_unit
```

This will also print out a coverage report as well as create an html coverage report. The long term goal would be >=75% coverage with unit tests, and more if possible of course! Right now that number is more like >=50%.

### Setting up Functional Test Environment


Executing the functional tests is a bit more complicated! First, thank you to Kristian Larsson for his great tool [vrnetlab](https://github.com/plajjan/vrnetlab)! All functional tests are built on this awesome platform that allows for easy creation of containerized network devices.

So far, basic functional tests exist for Cisco IOS-XE and Cisco NX-OS, these use the CSR1000v and Nexus 9000v virtual platforms respectively. vrnetlab currently only supports the older emulation style NX-OS devices, and *not* the newer VM image n9kv. I have made some very minor tweaks to vrnetlab locally in order to get the n9kv image running -- I hope to raise a PR to add this to vrnetlab in the near future. Minus the n9kv tweaks, getting going with vrnetlab is fairly straightforward -- simply follow Kristian's great readme docs. After creating the image(s) that you wish to test, rename the image to the following format:

```
ssh2net[PLATFORM]
```

The docker-compose file here will be looking for the container images matching this pattern, so this is an important bit! Right now for IOS-XE and NX-OS the container image names need to be:

```
ssh2netiosxe
ssh2netnxos
```

You can tag the image names on creation (following the vrnetlab readme docs), or create a new tag once the image is built:

```
docker tag [TAG OF IMAGE CREATED] ssh2netnxos
```

Once you have created the images, you can start the containers with a make command:

```
make start_dev_env
```

Conversely you can terminate the containers:

```
make stop_dev_env
```

To start a specific platform container:

```
make start_dev_env_iosxe
```

Substitute "iosxe" for the platform type you want to start.

The containers don't take too long to fire up, maybe a few minutes (running on my old macmini with Ubuntu, so not exactly a powerhouse!). Once booted up you can connect to their console or via SSH:

| Device        | Local IP      |
| --------------|---------------|
| iosxe         | 172.18.0.11   |
| nxos          | 172.18.0.12   |
| iosxr         | 172.18.0.13   |
| eos   (future)| 172.18.0.14   |
| junos         | 172.18.0.15   |

The console port for all devices is 5000, so to connect to the console of the iosxe device you can simply telnet to that port locally:

```
telnet 172.18.0.11 5000
```

Credentials for all devices use the default vrnetlab credentials:

Username: vrnetlab

Password: VR-netlab9

Once the container(s) are ready, you can use the make commands to execute tests as needed:

- `test_functional` will execute all currently implemented functional tests
- `test_all` will execute all currently implemented functional tests as well as the unit tests
- `test_iosxe` will execute all unit tests and iosxe functional tests
- `test_nxos` will execute all unit tests and nxos functional tests
- `test_junos` will execute all unit tests and junos functional tests
