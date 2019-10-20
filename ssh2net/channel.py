"""ssh2net.channel"""
import logging
import re
import sys
from typing import List, Optional, Tuple

from ssh2.exceptions import SocketRecvError, Timeout

from ssh2net.decorators import channel_timeout

if not sys.platform.startswith("win"):
    from ssh2net.decorators import operation_timeout
else:
    from ssh2net.decorators import operation_timeout_win as operation_timeout


channel_log = logging.getLogger("ssh2net_channel")
session_log = logging.getLogger("ssh2net_session")


class SSH2NetChannel:
    @staticmethod
    def _rstrip_all_lines(output: bytes) -> str:
        """
        Right strip all lines in provided output

        Args:
            output: bytes object to handle

        Returns:
            output: bytes object with each line right stripped

        Raises:
            N/A  # noqa

        """
        output = output.decode("unicode_escape").strip().splitlines()
        output = [line.rstrip() for line in output]
        return "\n".join(output)

    @staticmethod
    def _restructure_output(output: str, strip_prompt: bool = False) -> str:
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
        output = output.splitlines()
        # purge empty rows before actual output
        for row in output.copy():
            if row == "":
                output = output[1:]
            else:
                break
        # should improve -- simply peels the last line out of the list...
        if strip_prompt:
            output = output[:-1]
        output = "\n".join(output)
        return output

    @channel_timeout(Timeout)
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
            output += self.channel.read()[1]
        channel_log.debug(f"Read: {repr(output)}")
        # once the input has been fully written to channel; flush it and send return char
        self.channel.flush()
        self.channel.write(self.comms_return_char)
        channel_log.debug(f"Write (sending return character): {repr(self.comms_return_char)}")

    @channel_timeout(Timeout)
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
            output += self.channel.read()[1]
            channel_log.debug(f"Read: {repr(output)}")
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
    def _send_input(self, channel_input: str, strip_prompt: bool):
        """
        Send input to device and return results

        Args:
            channel_input: string input to write to channel
            strip_prompt: bool True/False for whether or not to strip prompt

        Returns:
            output: string of cleaned channel data

        Raises:
            N/A  # noqa

        """
        self._acquire_session_lock()
        session_log.debug(
            f"Attempting to send input: {channel_input}; strip_prompt: {strip_prompt}"
        )
        self.channel.flush()
        self.channel.write(channel_input)
        channel_log.debug(f"Write: {repr(channel_input)}")
        self._read_until_input(channel_input)
        output = self._read_until_prompt()
        self.session_lock.release_lock()
        return self._restructure_output(output, strip_prompt=strip_prompt)

    @operation_timeout("comms_operation_timeout")
    def _send_input_interact(
        self,
        channel_input: str,
        expectation: str,
        response: str,
        finale: str,
        hidden_response: bool = False,
    ) -> str:
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
        session_log.debug(
            f"Attempting to send input interact: {channel_input}; "
            f"expecting: {expectation}; responding: {response}; "
            f"with a finale: {finale}; hidden_response: {hidden_response}"
        )
        self.channel.flush()
        self.channel.write(channel_input)
        channel_log.debug(f"Write: {repr(channel_input)}")
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
        channel_log.debug(f"Write: {repr(response)}")
        self.channel.write(self.comms_return_char)
        channel_log.debug(f"Write (sending return character): {repr(self.comms_return_char)}")
        output += self._read_until_prompt(prompt=finale)
        self.session_lock.release_lock()
        return self._restructure_output(output)

    def open_and_execute(self, command: str):
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
        session_log.info(f"Attempting to open channel for command execution")
        if self._shell:
            self._channel_close()
        self._channel_open()
        output = b""
        channel_buff = 1
        session_log.debug(f"Channel open, executing command: {command}")
        self.channel.execute(command)
        while channel_buff > 0:
            try:
                channel_buff, data = self.channel.read()
                output += data
            except SocketRecvError:
                break
        output = self._rstrip_all_lines(output)
        result = self._restructure_output(output)
        self.close()
        session_log.info(f"Command executed, channel closed")
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
        session_log.info(f"Attempting to open interactive shell")
        # open the channel itself
        self._channel_open()
        # invoke a shell on the channel
        self._channel_invoke_shell()
        # pre-login handling if needed for things like wlc
        if self.comms_pre_login_handler:
            self.comms_pre_login_handler(self)
        # send disable paging if needed
        if self.comms_disable_paging:
            if callable(self.comms_disable_paging):
                self.comms_disable_paging(self)
            else:
                self.send_inputs(self.comms_disable_paging)
        self._session_keepalive()
        session_log.info("Interactive shell opened")

    @channel_timeout(Timeout)
    def get_prompt(self) -> bool:
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
        channel_log.debug(f"Write (sending return character): {repr(self.comms_return_char)}")
        while True:
            output = self.channel.read()[1].rstrip(b"\\")
            output = output.decode("unicode_escape").strip()
            channel_match = re.search(pattern, output)
            if channel_match:
                self.session.set_timeout(self.session_timeout)
                current_prompt = channel_match.group(0)
                return current_prompt

    def send_inputs(self, inputs, strip_prompt: Optional[bool] = True) -> List[bytes]:
        """
        Primary entry point to send data to devices in shell mode; accept inputs and return results

        Args:
            inputs: list of strings or string of inputs to send to channel
            strip_prompt: strip prompt or not, defaults to True (yes, strip the prompt)

        Returns:
            result: list of output from the input command(s)

        Raises:
            N/A  # noqa

        """
        if isinstance(inputs, str):
            inputs = [inputs]
        results = []
        for channel_input in inputs:
            output = self._send_input(channel_input, strip_prompt)
            results.append(output)
        return results

    def send_inputs_interact(self, inputs, hidden_response=False) -> List[Tuple[str, bytes]]:
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
