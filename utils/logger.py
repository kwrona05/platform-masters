from __future__ import annotations

import logging
import os
import sys

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
COLOR_FORMAT = "%(asctime)s | %(log_color)s%(levelname)s%(reset)s | %(name)s | %(message_log_color)s%(message)s%(reset)s"


def _build_handler() -> logging.Handler:
    handler = logging.StreamHandler(sys.stdout)
    try:
        from colorlog import ColoredFormatter

        formatter = ColoredFormatter(
            COLOR_FORMAT,
            datefmt="%H:%M:%S",
            secondary_log_colors={
                "message": {
                    "DEBUG": "cyan",
                    "INFO": "white",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                }
            },
            style="%",
        )
    except Exception:
        formatter = logging.Formatter(LOG_FORMAT, "%H:%M:%S")
    handler.setFormatter(formatter)
    return handler


root = logging.getLogger()
root.handlers.clear()
root.setLevel(LOG_LEVEL)
root.addHandler(_build_handler())

logger = logging.getLogger("platform-masters")
