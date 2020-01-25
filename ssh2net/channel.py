"""ssh2net.channel"""
import logging
import re
import sys
from typing import Callable, List, Optional, Tuple, Union

from ssh2net.decorators import channel_timeout
from ssh2net.result import SSH2NetResult
from ssh2net.session import SSH2NetSession

if not sys.platform.startswith("win"):
    from ssh2net.decorators import operation_timeout
else:
    from ssh2net.decorators import operation_timeout_win as operation_timeout


LOG_ADMIN = logging.getLogger("ssh2net_channel_admin")
LOG_RAW = logging.getLogger("ssh2net_channel_raw")


class SSH2NetChannel(SSH2NetSession):
    """
    SSH2NetChannel

    SSH2Net <- SSH2NetChannel <- SSH2NetSession <- SSH2NetSocket

    SSH2NetChannel is responsible for all channel input and output. SSH2NetChannel should not care
    about what is providing the channel. At time of writing the channel can be provided by
    ssh2-python or paramiko. The channel provided must provide the following methods:

        write:
            accept channel input as a string and write it to the channel

        read:
            read data from the channel

        flush:
            flush the channel -- pull all data off the channel basically

        close:
            close the channel object

    The channel object should also provide an `execute` method, though this is really only useful
    for ssh2-python at the moment so it could just raise a NotImplemented exception for that method.

    The following arguments are type hinted here at the base class. ssh2net uses a mixin type
    structure to divide each logical component of the overall ssh2net object into its own class.
    Because of the mixin structure there are no init methods in the Channel, Session, or Socket
    classes. In order to appease mypy and ensure that ssh2net is typed reasonably well the typing
    information for these classes are done at the class level as found here.

    """

    host: str
    setup_validate_host: bool
    setup_port: int
    setup_timeout: int
    setup_ssh_config_file: Union[str, bool]
    setup_use_paramiko: bool
    session_timeout: int
    session_keepalive: bool
    session_keepalive_interval: int
    session_keepalive_type: str
    session_keepalive_pattern: str
    auth_user: str
    auth_password: Optional[str]
    auth_public_key: Optional[str]
    comms_strip_ansi: bool
    comms_prompt_regex: str
    comms_operation_timeout: int
    comms_return_char: str
    comms_pre_login_handler: Callable
    comms_disable_paging: Union[str, Callable]

    @staticmethod
    def _rstrip_all_lines(output: bytes) -> str:
        """
        Right strip all lines in provided output

        Args:
            output: bytes object to handle

        Returns:
            output: str object with each line right stripped

        Raises:
            N/A  # noqa

        """
        split_output: List[str] = output.decode("unicode_escape").strip().splitlines()
        split_output = [line.rstrip() for line in split_output]
        rejoined_output = "\n".join(split_output)
        return rejoined_output

    @staticmethod
    def _strip_ansi(output: bytes) -> bytes:
        """
        Strip ansi characters from bytes string

        Args:
            output: bytes from channel that need ansi stripped

        Returns:
            output: bytes string with ansi stripped

        Raises:
            N/A  # noqa

        """
        ansi_escape_pattern = re.compile(rb"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        output = re.sub(ansi_escape_pattern, b"", output)
        return output

    def _restructure_output(self, output: str, strip_prompt: bool = False) -> str:
        """
        Clean up preceding empty lines, and strip prompt if desired

        Args:
            output: list of strings to parse
            strip_prompt: bool True/False whether to strip prompt or not

        Returns:
            output: string of joined output lines

        Raises:
            N/A  # noqa

        """
        split_output = output.splitlines()
        # purge empty rows before actual output
        for row in split_output.copy():
            if row == "":
                split_output = split_output[1:]
            else:
                break

        output = "\n".join(split_output)
        if strip_prompt:
            # could be compiled somewhere else, but this allows for users to modify the prompt on
            # the fly if they want to
            prompt_pattern = re.compile(self.comms_prompt_regex, flags=re.M | re.I)
            output = re.sub(prompt_pattern, "", output)
        return output

    @channel_timeout()
    def _read_until_input(self, channel_input: str) -> None:
        """
        Read until all input has been entered, then send return.

        strip off everything before and including the command

        Args:
            channel_input: string to write to channel

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        output = b""
        while channel_input.encode() not in output:
            if not self.comms_strip_ansi:
                output += self.channel.read()[1]
            else:
                output += self._strip_ansi(self.channel.read()[1])
        LOG_RAW.debug(f"Read: {repr(output)}")
        # once the input has been fully written to channel; flush it and send return char
        self.channel.flush()
        LOG_RAW.debug(f"Write (sending return character): {repr(self.comms_return_char)}")
        self.channel.write(self.comms_return_char)

    @channel_timeout()
    def _read_until_prompt(self, output=None, prompt=None):
        """
        Read the channel until the desired prompt is seen

        Args:
            output: bytes of previously seen output if any
            prompt: string of prompt to look for; refactor to prefer regex

        Returns:
            output: bytes of any channel reads after prompt has been seen

        Raises:
            N/A  # noqa

        """
        if not output:
            output = b""

        # prefer to use regex match where possible; assume pattern is regex if starting with
        # ^ or ending with $ -- this works as we always use multi line search
        if not prompt:
            prompt_pattern = re.compile(self.comms_prompt_regex, flags=re.M | re.I)
            prompt_regex = True
        else:
            if prompt.startswith("^") or prompt.endswith("$"):
                prompt_pattern = re.compile(prompt, flags=re.M | re.I)
                prompt_regex = True
            else:
                prompt_pattern = prompt
                prompt_regex = False

        # disabling session blocking means the while loop will actually iterate
        # without this iteration we can never properly check for prompts
        self.session.set_blocking(False)
        while True:
            if not self.comms_strip_ansi:
                output += self.channel.read()[1]
            else:
                output += self._strip_ansi(self.channel.read()[1])
            LOG_RAW.debug(f"Read: {repr(output)}")
            # we do not need to deal w/ line replacement for the actual output, only for
            # parsing if a prompt-like thing is at the end of the output
            output_copy = output
            output_copy = re.sub("\r", "\n", output_copy.decode("unicode_escape").strip())
            if prompt_regex:
                channel_match = re.search(prompt_pattern, output_copy)
            elif prompt in output_copy:
                channel_match = True
            else:
                channel_match = False
            if channel_match:
                output = self._rstrip_all_lines(output)
                self.session.set_blocking(True)
                return output

    @operation_timeout("comms_operation_timeout")
    def _send_input(self, channel_input: str, strip_prompt: bool) -> SSH2NetResult:
        """
        Send input to device and return results

        Args:
            channel_input: string input to write to channel
            strip_prompt: bool True/False for whether or not to strip prompt

        Returns:
            result: SSH2NetResult object

        Raises:
            N/A  # noqa

        """
        self._acquire_session_lock()
        result = SSH2NetResult(self.host, channel_input)
        LOG_ADMIN.debug(f"Attempting to send input: {channel_input}; strip_prompt: {strip_prompt}")
        self.channel.flush()
        LOG_RAW.debug(f"Write: {repr(channel_input)}")
        self.channel.write(channel_input)
        self._read_until_input(channel_input)
        output = self._read_until_prompt()
        self.session_lock.release()
        output = self._restructure_output(output, strip_prompt=strip_prompt)
        result.record_result(output)
        return result

    @operation_timeout("comms_operation_timeout")
    def _send_input_interact(
        self,
        channel_input: str,
        expectation: str,
        response: str,
        finale: str,
        hidden_response: bool = False,
    ) -> SSH2NetResult:
        """
        Respond to a single "staged" prompt and return results

        Args:
            channel_input: string input to write to channel
            expectation: string of what to expect from channel
            response: string what to respond to the "expectation"
            finale: string of prompt to look for to know when "done"
            hidden_response: True/False response is hidden (i.e. password input)

        Returns:
            output: string of cleaned channel data

        Raises:
            N/A  # noqa

        """
        self._acquire_session_lock()
        result = SSH2NetResult(self.host, channel_input)
        LOG_ADMIN.debug(
            f"Attempting to send input interact: {channel_input}; "
            f"\texpecting: {expectation};"
            f"\tresponding: {response};"
            f"\twith a finale: {finale};"
            f"\thidden_response: {hidden_response}"
        )
        self.channel.flush()
        self.channel.write(channel_input)
        LOG_RAW.debug(f"Write: {repr(channel_input)}")
        self._read_until_input(channel_input)
        output = self._read_until_prompt(prompt=expectation)
        # if response is simply a return; add that so it shows in output
        # likewise if response is "hidden" (i.e. password input), add return
        # otherwise, skip
        if not response:
            output += self.comms_return_char
        elif hidden_response is True:
            output += self.comms_return_char
        self.channel.write(response)
        LOG_RAW.debug(f"Write: {repr(response)}")
        self.channel.write(self.comms_return_char)
        LOG_RAW.debug(f"Write (sending return character): {repr(self.comms_return_char)}")
        output += self._read_until_prompt(prompt=finale)
        self.session_lock.release()
        output = self._restructure_output(output)
        result.record_result(output)
        return result

    @channel_timeout()
    def get_prompt(self) -> Union[str, bytes]:
        """
        Read from shell and get the current shell prompt

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        pattern = re.compile(self.comms_prompt_regex, flags=re.M | re.I)
        self.session.set_timeout(1000)
        self.channel.flush()
        self.channel.write(self.comms_return_char)
        LOG_RAW.debug(f"Write (sending return character): {repr(self.comms_return_char)}")
        while True:
            output = self.channel.read()[1].rstrip(b"\\")
            output = output.decode("unicode_escape").strip()
            channel_match = re.search(pattern, output)
            if channel_match:
                self.session.set_timeout(self.session_timeout)
                current_prompt = channel_match.group(0)
                return current_prompt

    def send_inputs(
        self, inputs: Union[str, List, Tuple], strip_prompt: Optional[bool] = True
    ) -> List[SSH2NetResult]:
        """
        Primary entry point to send data to devices in shell mode; accept inputs and return results

        Args:
            inputs: list of strings or string of inputs to send to channel
            strip_prompt: strip prompt or not, defaults to True (yes, strip the prompt)

        Returns:
            results: list of SSH2NetResult object(s)

        Raises:
            N/A  # noqa

        """
        if isinstance(inputs, str):
            inputs = [inputs]
        results = []
        for channel_input in inputs:
            result = self._send_input(channel_input, strip_prompt)
            results.append(result)
        return results

    def send_inputs_interact(self, inputs, hidden_response=False) -> List[SSH2NetResult]:
        """
        Primary entry point to interact with devices in shell mode; used to handle prompts

        accepts inputs and looks for expected prompt;
        sends the appropriate response, then waits for the "finale"
        returns the results of the interaction

        could be "chained" together to respond to more than a "single" staged prompt

        Args:
            inputs: tuple containing strings representing:
                initial input
                expectation (what should ssh2net expect after input)
                response (response to expectation)
                finale (what should ssh2net expect when "done")
            hidden_response: True/False response is hidden (i.e. password input)

        Returns:
            result: list of output from the input command(s)

        Raises:
            N/A  # noqa

        """
        if isinstance(inputs, tuple):
            inputs = [inputs]
        results = []
        for channel_input, expectation, response, finale in inputs:
            output = self._send_input_interact(
                channel_input, expectation, response, finale, hidden_response
            )
            results.append(output)
        return results

    def open_and_execute(self, command: str) -> str:
        """
        Open ssh channel and execute a command; closes channel when done.

        "one time use" method -- best for running one command then moving on; otherwise
        use "open_shell" instead, though this will likely be substantially faster for "single"
        operations.

        Args:
            command: string input to write to channel

        Returns:
            result: output from command sent over the channel

        Raises:
            N/A  # noqa

        """
        if self.setup_use_paramiko:
            raise NotImplementedError
        output = self._open_and_execute(command)
        stripped_output = self._rstrip_all_lines(output)
        result = self._restructure_output(stripped_output)
        return result

    def open_shell(self) -> None:
        """
        Open and prepare interactive SSH shell

        Args:
            N/A  # noqa

        Returns:
            N/A  # noqa

        Raises:
            N/A  # noqa

        """
        self._open_shell()
        # pre-login handling if needed for things like accepting login banners etc.
        if self.comms_pre_login_handler:
            self.comms_pre_login_handler(self)
        # send disable paging if needed
        if self.comms_disable_paging:
            if callable(self.comms_disable_paging):
                self.comms_disable_paging(self)
            else:
                self.send_inputs(self.comms_disable_paging)
        self._session_keepalive()
