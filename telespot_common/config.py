import os
from typing import Dict, Optional


def resolve_config_path(*, local_dir: Optional[str] = None) -> str:
    """Return the most appropriate config file path.

    Preference order:
    - `~/.telespot_config` if it exists (documented default)
    - `<local_dir>/.telespot_config` (legacy / portable mode)
    - `~/.telespot_config` as the default write target
    """

    home_path = os.path.expanduser("~/.telespot_config")
    local_base = local_dir if local_dir is not None else os.getcwd()
    local_path = os.path.join(local_base, ".telespot_config")

    if os.path.exists(home_path):
        return home_path
    if os.path.exists(local_path):
        return local_path
    return home_path


def read_simple_kv_config(path: str, defaults: Dict[str, str]) -> Dict[str, str]:
    """Read a simple `key=value` config file with `#` comments."""

    cfg = dict(defaults)
    if not os.path.exists(path):
        return cfg

    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                cfg[key.strip()] = value.strip()
    except Exception:
        # Preserve existing behavior: config load failure shouldn't crash.
        return cfg

    return cfg

