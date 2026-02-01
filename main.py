"""Entry point."""

import argparse
from src.bot import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Virtualizor Telegram Bot")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    run(debug=args.debug)
