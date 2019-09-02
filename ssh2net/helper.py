"""ssh2net.helper"""
import importlib


def validate_external_function(possible_function):
    """
    Validate string representing external function is a callable

    Args:
        possible_function: string "pointing" to external function

    Returns:
        None/Callable: None or callable function

    Raises:
        N/A

    """
    try:
        if not isinstance(possible_function, str):
            return None
        if "." not in possible_function:
            return None
        else:
            ext_func_path = possible_function.split(".")
            ext_module = ".".join(ext_func_path[:-1])
            ext_function = ext_func_path[-1]
            ext_module = importlib.import_module(ext_module)
            return getattr(ext_module, ext_function)
    except ModuleNotFoundError:
        return None
