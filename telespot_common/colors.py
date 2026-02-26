class Colors:
    """ANSI color codes used across both entrypoints.

    `telespot.py` historically used `END` while `telespotx.py` used `RESET`.
    Provide both for compatibility.
    """

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    BOLD = "\033[1m"
    DIM = "\033[2m"

    END = "\033[0m"
    RESET = END

    RAINBOW = ["\033[91m", "\033[93m", "\033[92m", "\033[96m", "\033[94m", "\033[95m"]

