"""ssh2net.ssh_config"""
import os
from pathlib import Path
import re
import shlex


class SSH2NetSSHConfig:
    def __init__(self, ssh_config_file=""):
        """
        Initialize SSH2NetSSHConfig Object

        Parse OpenSSH config file

        Try to load the following data for all entries in config file:
            Host
            HostName
            Port
            User
            AddressFamily
            BindAddress
            ConnectTimeout
            IdentitiesOnly
            IdentityFile
            KbdInteractiveAuthentication
            PasswordAuthentication
            PreferredAuthentications

        Args:
            ssh_config_file: string path to ssh configuration file to use if not provided
                will try to use users ssh config file in ~/.ssh/config first, then will try
                /etc/ssh/config_file

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self.ssh_config_file = self._select_config_file(ssh_config_file)
        if self.ssh_config_file:
            with open(self.ssh_config_file, "r") as f:
                self.ssh_config_file = f.read()
            self.hosts = self._parse()
            if not self.hosts:
                self.hosts = None
        else:
            self.hosts = None

    def __str__(self):
        """
        Magic str method for SSH2NetSSHConfig class

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        return "SSH2NetSSHConfig Object"

    def __repr__(self):
        """
        Magic repr method for SSH2NetSSHConfig class

        Args:
            N/A  # noqa

        Returns:
            repr: repr for class object

        Raises:
            N/A  # noqa

        """
        class_dict = self.__dict__.copy()
        del class_dict["ssh_config_file"]
        return f"SSH2NetSSHConfig {class_dict}"

    def __bool__(self):
        """
        Magic bool method; return True if ssh_config_file

        Args:
            N/A  # noqa

        Returns:
            bool: True/False if ssh_config_file

        Raises:
            N/A  # noqa

        """
        if self.ssh_config_file:
            return True
        return False

    @staticmethod
    def _select_config_file(ssh_config_file):
        """
        Select ssh configuration file

        Args:
            ssh_config_file: string representation of ssh config file to try to use

        Returns:
            ssh_config_file: Pathlib path object or None

        Raises:
            N/A  # noqa

        """
        if Path(ssh_config_file).is_file():
            return Path(ssh_config_file)
        if Path(os.path.expanduser("~/.ssh/config")).is_file():
            return Path(os.path.expanduser("~/.ssh/config"))
        if Path("/etc/ssh/ssh_config").is_file():
            return Path("/etc/ssh/ssh_config")
        return None

    @staticmethod
    def _strip_comments(line):
        """
        Strip out comments from ssh config file lines

        Args:
            line: to strip comments from

        Returns:
            line: rejoined ssh config file line after stripping comments

        Raises:
            N/A  # noqa

        """
        line = " ".join(shlex.split(line, comments=True))
        return line

    def _parse(self):
        """
        Parse SSH configuration file

        Args:
            N/A  # noqa

        Returns:
            discovered_hosts: dict of host objects discovered in ssh config file

        Raises:
            N/A  # noqa

        """

        # uncomment next line and handle global patterns (stuff before hosts) at some point
        # global_config_pattern = re.compile(r"^.*?\b(?=host)", flags=re.I | re.S)
        # use word boundaries with a positive lookahead to get everything between the word host
        # need to do this as whitespace/formatting is not really a thing in ssh_config file
        # match host\s to ensure we don't pick up hostname and split things there accidentally
        host_pattern = re.compile(r"\bhost.*?\b(?=host\s|\s+$)", flags=re.I | re.S)
        host_entries = re.findall(host_pattern, self.ssh_config_file)
        discovered_hosts = {}
        if not host_entries:
            return discovered_hosts

        # do we need to add whitespace between match and end of line to ensure we match correctly?
        hosts_pattern = re.compile(r"^\s*host[\s=]+(.*)$", flags=re.I | re.M)
        hostname_pattern = re.compile(r"^\s*hostname[\s=]+([\w.-]*)$", flags=re.I | re.M)
        port_pattern = re.compile(r"^\s*port[\s=]+([\d]*)$", flags=re.I | re.M)
        user_pattern = re.compile(r"^\s*user[\s=]+([\w]*)$", flags=re.I | re.M)
        # address_family_pattern = None
        # bind_address_pattern = None
        # connect_timeout_pattern = None
        identities_only_pattern = re.compile(
            r"^\s*identitiesonly[\s=]+(yes|no)$", flags=re.I | re.M
        )
        identity_file_pattern = re.compile(
            r"^\s*identityfile[\s=]+([\w.\/\@~-]*)$", flags=re.I | re.M
        )
        # keyboard_interactive_pattern = None
        # password_authentication_pattern = None
        # preferred_authentication_pattern = None

        for host_entry in host_entries:
            host = Host()
            host_line = re.search(hosts_pattern, host_entry)
            if host_line:
                host.hosts = self._strip_comments(host_line.groups()[0])
            hostname = re.search(hostname_pattern, host_entry)
            if hostname:
                host.hostname = self._strip_comments(hostname.groups()[0])
            port = re.search(port_pattern, host_entry)
            if port:
                host.port = self._strip_comments(port.groups()[0])
            user = re.search(user_pattern, host_entry)
            if user:
                host.user = self._strip_comments(user.groups()[0])
            # address_family = re.search(user_pattern, host_entry[0])
            # bind_address = re.search(user_pattern, host_entry[0])
            # connect_timeout = re.search(user_pattern, host_entry[0])
            identities_only = re.search(identities_only_pattern, host_entry)
            if identities_only:
                host.identities_only = self._strip_comments(identities_only.groups()[0])
            identity_file = re.search(identity_file_pattern, host_entry)
            if identity_file:
                host.identity_file = self._strip_comments(identity_file.groups()[0])
            # keyboard_interactive = re.search(user_pattern, host_entry[0])
            # password_authentication = re.search(user_pattern, host_entry[0])
            # preferred_authentication = re.search(user_pattern, host_entry[0])
            discovered_hosts[host.hosts] = host
        return discovered_hosts

    def _lookup_fuzzy_match(self, host):
        """
        Look up fuzzy matched hosts

        Get the best match ssh config Host entry for a given host; this allows for using
        the splat and question-mark operators in ssh config file

        Args:
            host: host to lookup in discovered_hosts dict

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        possible_matches = []
        for host_entry in self.hosts.keys():
            host_list = host_entry.split()
            for host_pattern in host_list:
                # replace periods with literal period
                # replace asterisk (match 0 or more things) with appropriate regex
                # replace question mark (match one thing) with appropriate regex
                host_pattern = (
                    host_pattern.replace(".", r"\.").replace("*", r"(.*)").replace("?", r"(.)")
                )
                # compile with case insensitive
                host_pattern = re.compile(host_pattern, flags=re.I)
                result = re.search(host_pattern, host)
                # if we get a result, append it and the original pattern to the possible matches
                if result:
                    possible_matches.append((result, host_entry))
        # initialize a None best match
        best_match = None
        for match in possible_matches:
            if best_match is None:
                best_match = match
            # count how many chars were replaced to get regex to work
            chars_replaced = 0
            for start_char, end_char in match[0].regs[1:]:
                chars_replaced += end_char - start_char
            # count how many chars were replaced to get regex to work on best match
            best_match_chars_replaced = 0
            for start_char, end_char in best_match[0].regs[1:]:
                best_match_chars_replaced += end_char - start_char
            # if match replaced less chars than "best_match" we have a new best match
            if chars_replaced < best_match_chars_replaced:
                best_match = match
        return self.hosts[best_match[1]]

    def lookup(self, host):
        """
        Lookup a given host

        Args:
            host: host to lookup in discovered_hosts dict

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        # return exact 1:1 match if exists
        if host in self.hosts.keys():
            return self.hosts[host]
        # return match if given host is an exact match for a host entry
        for host_entry in self.hosts.keys():
            host_list = host_entry.split()
            if host in host_list:
                return self.hosts[host_entry]
        # otherwise need to select the most correct host entry
        return self._lookup_fuzzy_match(host)


class Host:
    def __init__(self):
        """
        Initialize SSH2Net Host Object

        Create a Host object based on ssh config file information
        """
        self.hosts = None
        self.hostname = None
        self.port = None
        self.user = None
        self.address_family = None
        self.bind_address = None
        self.connect_timeout = None
        self.identities_only = None
        self.identity_file = None
        self.keyboard_interactive = None
        self.password_authentication = None
        self.preferred_authentication = None

    def __str__(self):
        """
        Magic str method for HostEntry class

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        return f"Host: {self.hosts}"

    def __repr__(self):
        """
        Magic repr method for HostEntry class

        Args:
            N/A  # noqa

        Returns:
            repr: repr for class object

        Raises:
            N/A  # noqa

        """
        class_dict = self.__dict__.copy()
        return f"HostEntry {class_dict}"
