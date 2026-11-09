# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Base module for pytest-oarepo.

This module provides testing utilities and fixtures in OARepo applications.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pytest-oarepo")
except PackageNotFoundError:
    __version__ = "0.0.0dev0+unknown"

__all__ = [
    "__version__",
]
