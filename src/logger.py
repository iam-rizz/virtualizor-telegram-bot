"""Custom logger configuration."""

import logging
import sys
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and clean output."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    def format(self, record):
        # Time
        time_str = datetime.now().strftime("%H:%M:%S")

        # Level with color
        color = self.COLORS.get(record.levelname, self.RESET)
        level = f"{color}{record.levelname:>7}{self.RESET}"

        # Module name (shortened)
        name = record.name.split(".")[-1][:12].ljust(12)

        # Message
        msg = record.getMessage()

        return f"{self.DIM}{time_str}{self.RESET} {level} {self.DIM}{name}{self.RESET} {msg}"


def setup_logger():
    """Configure application logging."""
    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)

    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Console handler with custom formatter
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(ColoredFormatter())
    root.addHandler(console)

    return logging.getLogger("bot")


def print_banner():
    """Print startup banner."""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║     Virtualizor Telegram Bot v1.0.0       ║
    ║     ─────────────────────────────────     ║
    ║     VM Management via Telegram            ║
    ╚═══════════════════════════════════════════╝
    """
    print(banner)
