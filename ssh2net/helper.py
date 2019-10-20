"""ssh2net.helper"""
import importlib
from io import TextIOWrapper
import pkg_resources  # pylint: disable=C0411
import warnings


def validate_external_function(possible_function):
    """
    Validate string representing external function is a callable

    Args:
        possible_function: string "pointing" to external function

    Returns:
        None/Callable: None or callable function

    Raises:
        N/A  # noqa

    """
    try:
        if not isinstance(possible_function, str):
            return None
        if "." not in possible_function:
            return None
        ext_func_path = possible_function.split(".")
        ext_module = ".".join(ext_func_path[:-1])
        ext_function = ext_func_path[-1]
        ext_module = importlib.import_module(ext_module)
        return getattr(ext_module, ext_function)
    except ModuleNotFoundError:
        return None


def _textfsm_get_template(platform: str, command: str):
    """
    Find correct TextFSM template based on platform and command executed

    Args:
        platform: ntc-templates device type; i.e. cisco_ios, arista_eos, etc.
        command: string of command that was executed (to find appropriate template)

    Returns:
        None or TextIOWrapper of opened template

    """
    try:
        from textfsm.clitable import CliTable  # noqa
        import ntc_templates  # noqa
    except ModuleNotFoundError as exc:
        err = f"Module '{exc.name}' not installed!"
        msg = f"***** {err} {'*' * (80 - len(err))}"
        fix = (
            f"To resolve this issue, install '{exc.name}'. You can do this in one of the following"
            " ways:\n"
            "1: 'pip install -r requirements-textfsm.txt'\n"
            "2: 'pip install ssh2net[textfsm]'"
        )
        warning = "\n" + msg + "\n" + fix + "\n" + msg
        warnings.warn(warning)
        return None
    template_dir = pkg_resources.resource_filename("ntc_templates", "templates")
    cli_table = CliTable("index", template_dir)
    template_index = cli_table.index.GetRowMatch({"Platform": platform, "Command": command})
    if not template_index:
        return None
    template_name = cli_table.index.index[template_index]["Template"]
    template = open(f"{template_dir}/{template_name}")
    return template


def textfsm_parse(template, output):
    """
    Parse output with TextFSM and ntc-templates, try to return structured output

    Args:
        template: TextIOWrapper or string path to template to use to parse data
        output: unstructured output from device to parse

    Returns:
        output: structured data

    """
    import textfsm  # noqa

    if not isinstance(template, TextIOWrapper):
        template = open(template)
    re_table = textfsm.TextFSM(template)
    try:
        output = re_table.ParseText(output)
        return output
    except textfsm.parser.TextFSMError:
        pass
    return output
