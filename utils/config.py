import os
import re
import dotenv
import yaml

ENV_PATTERN = re.compile(r"\$\{([^}^{]+)\}")

def _expand_env_vars(value: str) -> str:
    """
    Expand ${VAR} and ${VAR:-default} in a string using os.environ.
    Raises KeyError if VAR is missing and no default is provided.
    """
    def replacer(match):
        expr = match.group(1)
        if ":-" in expr:
            var, default = expr.split(":-", 1)
            return os.environ.get(var, default)
        else:
            if expr not in os.environ:
                raise KeyError(f"Missing required environment variable: {expr}")
            return os.environ[expr]

    return ENV_PATTERN.sub(replacer, value)

def _walk_and_expand(obj):
    """Recursively expand env vars in nested dict/list/str values."""
    if isinstance(obj, dict):
        return {k: _walk_and_expand(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_walk_and_expand(v) for v in obj]
    elif isinstance(obj, str):
        return _expand_env_vars(obj)
    else:
        return obj

def load_config(path="config.yaml") -> dict:
    dotenv.load_dotenv()

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    return _walk_and_expand(data)
