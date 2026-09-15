import logging
import sys
from typing import Optional


def setup_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger("business_report")
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(handler)
    root.setLevel(level)
    root.propagate = False


def get_logger(name: Optional[str] = None) -> logging.Logger:
    if name:
        return logging.getLogger(f"business_report.{name}")
    return logging.getLogger("business_report")
