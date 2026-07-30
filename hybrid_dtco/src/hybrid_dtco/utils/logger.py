# Copyright (c) 2026 NVIDIA + Synopsys + Google DeepMind.
# All rights reserved.
# Licensed under the Apache License, Version 2.0.

"""
Module defining the centralized logging infrastructure.
"""

import logging
import sys
from typing import Optional


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Constructs and returns a standard logger configured for industrial pipelines.

    Args:
        name: Name of the logger (usually __name__).
        level: Logging level.

    Returns:
        Configured standard logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger
