import logging
import sys
from datetime import datetime

from src.version import __version__


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    def format(self, record):
        time_str = datetime.now().strftime("%H:%M:%S")
        color = self.COLORS.get(record.levelname, self.RESET)
        level = f"{color}{record.levelname:>7}{self.RESET}"
        name = record.name.split(".")[-1][:12].ljust(12)
        msg = record.getMessage()
        return f"{self.DIM}{time_str}{self.RESET} {level} {self.DIM}{name}{self.RESET} {msg}"


def setup_logger():
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    for handler in root.handlers[:]:
        root.removeHandler(handler)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(ColoredFormatter())
    root.addHandler(console)

    return logging.getLogger("bot")


def print_banner():
    banner = f"""
    \033[36m╔═══════════════════════════════════════════╗
    ║\033[0m   \033[1mVirtualizor Telegram Bot v{__version__}\033[0m        \033[36m ║
    ║\033[0m   ─────────────────────────────────────   \033[36m║
    ║\033[0m   VM Management via Telegram              \033[36m║
    ║\033[0m   github.com/iam-rizz                     \033[36m║
    ╚═══════════════════════════════════════════╝\033[0m
    """
    print(banner)
