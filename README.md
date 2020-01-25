![](https://github.com/carlmontanari/ssh2net/workflows/build/badge.svg)
[![PyPI version](https://badge.fury.io/py/ssh2net.svg)](https://badge.fury.io/py/ssh2net)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

ssh2net
=======

Python library for connecting to devices, specifically network devices (routers/switches/etc.) via SSH. ssh2net is
 built primarily on, and intended to be used with [ssh2-python](https://github.com/ParallelSSH/ssh2-python) as the
  underlying transport. ssh2-python provides bindings to [libssh2](https://github.com/libssh2/libssh2). ssh2net also
   supports using [paramiko](https://github.com/paramiko/paramiko) for the underlying transport due to some
    limitations/lack of updates in ssh2-python. 

ssh2net is focused on being lightweight and pluggable so that it *should* be flexible enough to be adapted to handle
 connecting to, sending commands to, and reading output from most any network device with a traditional SSH driven CLI.


# Table of Contents

- [Documentation](#documentation)
- [Supported Platforms](#supported-platforms)
- [Installation](#installation)
- [Examples Links](#examples-links)
- [Basic Usage](#basic-usage)
  - [Native and Platform Drivers Examples](#native-and-platform-drivers-examples)
  - [Platform Regex](#platform-regex)
  - [Basic Operations -- Sending and Receiving](#basic-operations----sending-and-receiving)
  - [Result Objects](#result-objects)
  - [Handling Prompts](#handling-prompts)
  - [Driver Privilege Levels](#driver-privilege-levels)
  - [Sending Configurations](#sending-configurations)
  - [TextFSM/NTC-Templates Integration](#textfsmntc-templates-integration)
  - [Timeouts](#timeouts)
  - [Disabling Paging](#disabling-paging)
  - [Login Handlers](#login-handlers)
  - [SSH Config Support](#ssh-config-support)
- [FAQ](#faq)
- [Linting and Testing](#linting-and-testing)


# Documentation

Documentation is auto-generated [using pdoc3](https://github.com/pdoc3/pdoc). Documentation is linted (see Linting and Testing section) via [pydocstyle](https://github.com/PyCQA/pydocstyle/) and [darglint](https://github.com/terrencepreilly/darglint).

Documentation is hosted via GitHub Pages and can be found [here.](https://carlmontanari.github.io/ssh2net/docs/ssh2net/index.html) You can also view the readme as a web page [here.](https://carlmontanari.github.io/ssh2net/)

To regenerate documentation locally, use the following make command:

```
make docs
```


# Supported Platforms

ssh2net is all built on a basic SSH2Net connection. This SSH2Net object provides all of the basic SSH connection
 "stuff" without much else at all. The SSH2Net object will open a socket, an SSH session, authenticate that session
 , and send and receive data on an SSH channel. All of this is focused on network device type SSH cli interfaces, but
  should work on pretty much any SSH connection (though there are almost certainly better options for non-network
   type devices!). This "base" connection does not handle any kind of device-specific operations such as privilege
    escalation or saving configurations, it is simply intended to be a bare bones connection that can interact with
     nearly any device/platform if you are willing to send/parse inputs/outputs manually.

On top of the "base" class ssh2net has the concept of "drivers" -- pretty much exactly like the implementation in
 [NAPALM](https://github.com/napalm-automation/napalm). The idea of a driver is that it extends the base class with
  device specific functionality such as privilege escalation/de-escalation, setting appropriate prompts to search for
  , and picking out appropriate [ntc templates](https://github.com/napalm-automation/napalm) for use with TextFSM. 
  
At the moment there are five "core" drivers representing the most common networking platforms (outlined below)
, however in the future it would be possible for folks to contribute additional "community" drivers. It is unlikely
 that any additional "core" platforms would be added at the moment.

- Cisco IOS-XE (tested on: 16.04.01)
- Cisco NX-OS (tested on: 9.2.4)
- Juniper JunOS (tested on: 17.3R2.10)
- Cisco IOS-XR (tested on: 6.5.3)
- Arista EOS (tested on: 4.22.1F)*

*NOTE*: Arista EOS uses keyboard interactive authentication which is currently broken in the pip-installable version
 of ssh2-python. GitHub user [Red-M](https://github.com/Red-M) has contributed to and fixed this particular issue but
  the fix has not been merged. If you would like to use ssh2-python with EOS I suggest cloning and installing via Red
  -M's repository or my fork of Red-M's fork!

The goal for all "core" devices will be to include functional tests that can run against [vrnetlab](https://github.com/plajjan/vrnetlab) containers to
 ensure that the "core" devices are as thoroughly tested as is practical. 


# Installation

You should be able to pip install it "normally":

```
pip install ssh2net
```

To install from this repositories master branch:

```
pip install git+https://github.com/carlmontanari/ssh2net
```

To install from source:

```
git clone https://github.com/carlmontanari/ssh2net
cd ssh2net
python setup.py install
```

As for platforms to *run* ssh2net on -- it has and will be tested on MacOS and Ubuntu regularly and should work on any POSIX system. It has had minimal testing on Windows, however I have no plans on supporting Windows as I don't have access or desire to do so. In general I believe everything other than the TextFSM support should work though!


# Examples Links

- [Basic "native" SSH2Net operations](/examples/basic_usage/basic_usage_ssh2net_native_style.py)
- [Basic "driver" SSH2Net operations](/examples/basic_usage/basic_usage_ssh2net_driver_style.py)
- [Basic "ConnectHandler" (i.e. Netmiko) SSH2Net operations](/examples/basic_usage/basic_usage_ssh2net_connecthandler_style.py)
- [Setting up basic logging](/examples/logging/basic/basic.py)
- [Setting up separate log files](/examples/logging/separate_files/log_to_different_files.py)
- [Using SSH Key for authentication](/examples/ssh_keys/ssh_key_basic.py)


# Basic Usage

## Native and Platform Drivers Examples

Example SSH2Net "native/base" connection:

```python
from ssh2net import SSH2Net

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}
conn = SSH2Net(**my_device)
conn.open_shell()
```

Example IOS-XE driver setup. This also shows using context manager which is also supported on "native" mode -- when
 using the context manager there is no need to call the "open_shell" method:

```python
from ssh2net.core import IOSXEDriver

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}
with IOSXEDriver(**my_device) as conn:
    print(conn)
    # do stuff!
```


## Platform Regex

Due to the nature of SSH there is no good way to know when a command has completed execution. Put another way, when
 sending any command, data is returned over a socket, that socket doesn't ever tell us when it is "done" sending the
  output from the command that was executed. In order to know when the session is "back at the base prompt/starting
   point" ssh2net uses a regular expression pattern to find that base prompt.

This pattern is contained in the `comms_prompt_regex` setting, and is perhaps the most important argument to getting
 SSH2Net working.

The "base" (default, but changeable) pattern is:

`"^[a-z0-9.\-@()/:]{1,20}[#>$]$"`

*NOTE* all `comms_prompt_regex` should use the start and end of line anchors as all regex searches in ssh2net are
 multline (this is an important piece to making this all work!).

The above pattern works on all "core" platforms listed above for at the very least basic usage. Custom prompts or
 hostnames could in theory break this, so be careful!

If you do not wish to match Cisco "config" level prompts you could use a `comms_prompt_regex` such as:

`"^[a-z0-9.-@]{1,20}[#>$]$"`

If you use a platform driver, the base prompt is set in the driver so you don't really need to worry about this!

The `comms_prompt_regex` pattern can be changed at any time at or after instantiation of an ssh2net object. Changing
 this *can* break things though, so be careful!
 

## Basic Operations -- Sending and Receiving

Sending inputs and receiving outputs all ultimately is done through the base SSH2net object. The following example
 shows sending a "show version" command as a string. Also shown: `send_inputs` accepts a list/tuple of commands.

```python
from ssh2net import SSH2Net

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}
with SSH2Net(**my_device) as conn:
    results = conn.send_inputs("show version")
    results = conn.send_inputs(("show version", "show run"))
```

When using a network "driver", it is more desirable to use the `send_commands` method to send commands (commands that
 would be ran at privilege exec in Cisco terms). `send_commands` is just a thin wrapper around `send_inputs`, however
  it ensures that the device is at the appropriate prompt (`default_desired_priv` attribute of the specific driver
  , see [Driver Privilege Levels](#driver-privilege-levels)).

```python
from ssh2net.core import IOSXEDriver

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}
with IOSXEDriver(**my_device) as conn:
    results = conn.send_commands("show version")
    results = conn.send_inputs(("show version", "show run"))
```


## Result Objects

The `send_inputs` method (used directly, or via `send_commands` in a network driver) returns a list of `SSH2NetResult`
 objects. The `SSH2NetResult` object contains attributes for the command sent (`channel_input`), start/end/elapsed
  time, and of course the result of the command sent.

```python
from ssh2net.core import IOSXEDriver

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}
with IOSXEDriver(**my_device) as conn:
    results = conn.send_commands("show version")
    print(results[0].elapsed_time)
    print(results[0].result)
```


## Handling Prompts

In some cases you may need to run an "interactive" command on your device. The `send_inputs_interact` method can be
 used to handle these situations. This method accepts a tuple containing the initial input (command) to send, the
  expected prompt after the initial send, the response to that prompt, and the final expected prompt -- basically
   telling ssh2net when it is done with the interactive command. In the below example the expectation is that the
    current/base prompt is the final expected prompt, so we can simply call the `get_prompt` method to snag that
     directly off the router.

```python
from ssh2net.core import IOSXEDriver

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}
interact = ["clear logging", "Clear logging buffer [confirm]", "\n"]

with IOSXEDriver(**my_device) as conn:
    interactive = conn.send_inputs_interact(
                ("clear logging", "Clear logging buffer [confirm]", "\n", conn.get_prompt())
            )
```


## Driver Privilege Levels

The "core" drivers understand the basic privilege levels of their respective device types. As mentioned previously
, the drivers will automatically attain the "privilege_exec" (or equivalent) privilege level prior to executing "show
" commands. If you don't want this "auto-magic" you can use the base driver (SSH2Net). The privileges for each device
 are outlined in named tuples in the platforms `driver.py` file. 
 
As an example, the following privilege levels are supported by the IOSXEDriver:

1. "exec"
2. "privilege_exec"
3. "configuration"
4. "special_configuration"

Each privilege level has the following attributes:

- pattern: regex pattern to associate prompt to privilege level with
- name: name of the priv level, i.e. "exec"
- deescalate_priv: name of next lower privilege or None
- deescalate: command to deescalate to next lower privilege or None
- escalate: name of next higher privilege or None
- escalate_auth: command to escalate to next higher privilege or None
- escalate_prompt: False or pattern to expect for escalation -- i.e. "Password:"
- requestable: True/False if the privilege level is requestable
- level: integer value of level i.e. 1

If you wish to manually enter a privilege level you can use the `acquire_priv` method, passing in the name of the
 privilege level you would like to enter. In general you probably won't need this too often though as the driver
  should handle much of this for you.

```python
from ssh2net.core import IOSXEDriver

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}
interact = ["clear logging", "Clear logging buffer [confirm]", "\n"]

with IOSXEDriver(**my_device) as conn:
    conn.acquire_priv("configuration")
```


## Sending Configurations

When using the native mode (SSH2Net), sending configurations is no different than sending commands and is done via
 the `send_inputs` method. You must manually ensure you are in the correct privilege/mode.
 
When using any of the core drivers, you can send configurations via the `send_configs` method which will handle
 privilege escalation for you. As with the `send_commands` and `send_inputs` methods -- you can send a single string
  or a list/tuple of strings.

```python
from ssh2net.core import IOSXEDriver

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}
interact = ["clear logging", "Clear logging buffer [confirm]", "\n"]

with IOSXEDriver(**my_device) as conn:
    conn.send_commands(("interface loopback123", "description configured by ssh2net"))
```


## TextFSM/NTC-Templates Integration

ssh2net supports parsing output with TextFSM. This of course requires installing TextFSM and having ntc-templates
 somewhere on your system. When using a driver you can pass `textfsm=True` to the `send_commands` method to
  automatically try to parse all output. Parsed/structured output is stored in the `SSH2NetResult` object in the
   `structured_result` attribute. Alternatively you can use the `textfsm_parse_output` method of the driver to parse
    output in a more manual fashion. This method accepts the string command (channel_input) and the text result and
     returns structured data; the driver is already configured with the ntc-templates device type to find the correct
      template. 

```python
from ssh2net.core import IOSXEDriver

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}
interact = ["clear logging", "Clear logging buffer [confirm]", "\n"]

with IOSXEDriver(**my_device) as conn:
    results = conn.send_commands("show version", textfsm_parse=True)
    print(results[0].structured_result)
    # or parse manually...
    results = conn.send_command("show version")
    structured_output = conn.textfsm_parse_output("show version", results[0].result)
```

ssh2net also supports passing in templates manually (meaning not using the pip installed ntc-templates directory to
 find templates) if desired. The `ssh2net.helper.textfsm_parse` function accepts a string or loaded (TextIOWrapper
 ) template and output to parse. This can be useful if you have custom or one off templates or don't want to pip
  install ntc-templates.
  
```python
from ssh2net import SSH2Net
from ssh2net.helper import textfsm_parse

my_device = {"setup_host": "172.18.0.11", "auth_user": "vrnetlab", "auth_password": "VR-netlab9"}

with SSH2Net(**my_device) as conn:
    results = conn.send_inputs("show version")
    structured_result = textfsm_parse("/path/to/my/template", results[0].result)
```

*NOTE*: If a template does not return structured data an empty dict will be returned!


## Timeouts

ssh2net supports three different timeout settings.

1. `setup_timeout`:
    - This governs the underlying socket timeout and is set in seconds.
2. `session_timeout`:
    - This governs the time in milliseconds for each read operation.
    - This is basically the ssh2-python or paramiko timeout setting. If there is no response from the remote device for
   this duration the underlying driver will raise a timeout.
    - When this timer expires a decorator will catch the exception raised from the driver and a basic backoff algorithm
   is triggered. This algorithm will retry five times with a starting delay of 0.1 and a backoff of 2 seconds.
      - Set this timer with this in mind, or just leave the default which seems to work well enough!
    - If setting this to `0` the sessions are blocking and will be "forever" (with the caveat that the following
    timeout will also raise an exception if set!)
3. `comms_operation_timeout`:
    - This governs the timeout for any given "operation" -- where an operation is any command being sent via
   `send_inputs` or `send_inputs_interact`


## Disabling Paging

ssh2net native driver attempts to send `terminal length 0` to disable paging by default. In the future this will
 likely be removed and relegated to the device drivers only. For all drivers, there is a standard disable paging
  string already configured for you, however this is of course user configurable. In addition to passing a string to
   send to disable paging, ssh2net supports passing a callable. This callable should accept the drivers reference to
    self as the only argument. This allows for users to create a custom function to disable paging however they like
    . This callable option is supported on the native driver as well. In general it is probably a better idea to
     handle this by simply passing a string, but the goal is to be flexible so the callable is supported.
    
```python
from ssh2net.core import IOSXEDriver

def iosxe_disable_paging(cls):
    cls.send_inputs("term length 0")

my_device = {"setup_host": "1.2.3.4", "setup_ssh_config_file": "~/.ssh/config", "comms_disable_paging": iosxe_disable_paging}

with IOSXEDriver(**my_device) as conn:
    print(conn.get_prompt())
```


## Login Handlers

Some devices have additional prompts or banners at login. This generally causes issues for SSH screen scraping
 automation. ssh2net supports -- just like disable paging -- passing a string to send or a callable to execute after
  successful SSH connection but before disabling paging occurs. By default this is an empty string which does nothing.


## SSH Config Support

ssh2net supports some basic OpenSSH configuration file settings, but not all. The `setup_ssh_config_file` argument
 accepts a bool or a string. If passing a string, ssh2net will try to open the path represented by the string
  (supports `~/` expanduser), if passing `True` ssh2net will try to open the default system SSH config file in `/etc
  /ssh/ssh_config`. The SSH config file is then parsed to find the most accurate match for the host the connection is
   for. At the moment only `port`, `user` and `identity_file` are gleaned and loaded from the SSH config file
   , however the ground work has been laid to parse more of the config file. 

```python
from ssh2net.core import IOSXEDriver

my_device = {"setup_host": "1.2.3.4", "setup_ssh_config_file": "~/.ssh/config"}

with IOSXEDriver(**my_device) as conn:
    print(conn.get_prompt())
```

*Note* In this case I have user and identity file configured so I can ignore passing those arguments to the driver.


# FAQ

- Question: Why build this? Netmiko exists, Paramiko exists, Ansible exists, etc...?
  - Answer: To learn and build hopefully a really cool thing! While I think in general that SSH "screen scraping" is
   not "sexy" or even "good", it is the lowest common denominator for automation in the networking world. So I
    figured I could try to make the fastest, most flexible library around for SSH network automation! 
- Question: Is this better than Netmiko/Paramiko/Ansible?
  - Answer: Nope! It is different though! The main focus is just to be stupid fast. It is very much that. It *should
  * be super reliable too as the timeouts are very easy/obvious to control, and it should also be very very very easy
   to adapt to any other network-y type CLI.
- Question: Is this easy to use?
  - Answer: Yep! The "native" usage is pretty straight forward -- the thing to remember is that it doesn't do "things" for you like Netmiko does for example, so its a lot more like Paramiko in that regard. That said you can use one of the available drivers to have a more Netmiko-like experience -OR- write your own driver as this has been built with the thought of being easily extended.
- Other questions? Ask away!


# Linting and Testing

## Linting

This project uses [black](https://github.com/psf/black) for auto-formatting. In addition to black, tox will execute [pylama](https://github.com/klen/pylama), and [pydocstyle](https://github.com/PyCQA/pydocstyle) for linting purposes. I have began playing with adding type hinting and testing this with [mypy](https://github.com/python/mypy), however I've not added this to tox at this point. I've also added docstring linting with [darglint](https://github.com/terrencepreilly/darglint) which has been quite handy!

All commits to this repository will trigger a GitHub action which runs tox, but of course its nicer to just run that before making a commit to ensure that it will pass all tests!


### Typing

I hope to fully type this and add mypy to the linting process. At this point its definitely not there, but it is at
 least somewhat typed... hopefully more to come!


## Testing

I broke testing into two main categories -- unit and functional. Unit is what you would expect -- unit testing the code. Functional testing connects to virtual devices in order to more accurately test the code.


### Unit Tests

Unit tests can be executed via pytest:

```
python -m pytest tests/unit/
```

Or using the following make command:

```
make test_unit
```

This will also print out a coverage report as well as create an html coverage report. The long term goal would be >=75% coverage with unit tests, and more if possible of course! Right now that number is more like >=50%.


### Setting up Functional Test Environment


Executing the functional tests is a bit more complicated! First, thank you to Kristian Larsson for his great tool [vrnetlab](https://github.com/plajjan/vrnetlab)! All functional tests are built on this awesome platform that allows for easy creation of containerized network devices.

Basic functional tests exist for all "core" platform types (IOSXE, NXOS, IOSXR, EOS, Junos). Vrnetlab currently only supports the older emulation style NX-OS devices, and *not* the newer VM image n9kv. I have made some very minor tweaks to vrnetlab locally in order to get the n9kv image running -- I have raised a PR to add this to vrnetlab proper. Minus the n9kv tweaks, getting going with vrnetlab is fairly straightforward -- simply follow Kristian's great readme docs. For the Arista EOS image -- prior to creating the container you should boot the device and enter the `zerotouch disable` command. This allows for the config to actually be saved and prevents the interfaces from cycling through interface types in the container (I'm not clear why it does that but executing this command before building the container "fixes" this!). After creating the image(s) that you wish to test, rename the image to the following format:

```
ssh2net[PLATFORM]
```

The docker-compose file here will be looking for the container images matching this pattern, so this is an important bit! The container image names should be:

```
ssh2netiosxe
ssh2netnxos
ssh2netiosxr
ssh2netjunos
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

Most of the containers don't take too long to fire up, maybe a few minutes (running on my old macmini with Ubuntu, so not exactly a powerhouse!). That said, the IOS-XR device takes about 15 minutes to go to "healthy" status. Once booted up you can connect to their console or via SSH:

| Device        | Local IP      |
| --------------|---------------|
| iosxe         | 172.18.0.11   |
| nxos          | 172.18.0.12   |
| iosxr         | 172.18.0.13   |
| eos           | 172.18.0.14   |
| junos         | 172.18.0.15   |

The console port for all devices is 5000, so to connect to the console of the iosxe device you can simply telnet to that port locally:

```
telnet 172.18.0.11 5000
```

Credentials for all devices use the default vrnetlab credentials:

Username: `vrnetlab`

Password: `VR-netlab9`

Once the container(s) are ready, you can use the make commands to execute tests as needed:

- `test_functional` will execute all currently implemented functional tests
- `test_all` will execute all currently implemented functional tests as well as the unit tests
- `test_iosxe` will execute all unit tests and iosxe functional tests
- `test_nxos` will execute all unit tests and nxos functional tests
- `test_iosxr` will execute all unit tests and iosxr functional tests
- `test_junos` will execute all unit tests and junos functional tests
