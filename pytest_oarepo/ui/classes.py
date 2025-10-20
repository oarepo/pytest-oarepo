#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI classes for pytest-oarepo."""

from __future__ import annotations

from typing import override

from flask_webpackext.manifest import (
    JinjaManifest,
    JinjaManifestEntry,
    JinjaManifestLoader,
)


#
# Mock the webpack manifest to avoid having to compile the full assets.
#
class MockJinjaManifest(JinjaManifest):
    """Mock manifest."""

    def __getitem__(self, key: str) -> JinjaManifestEntry:
        """Get a manifest entry."""
        return JinjaManifestEntry(key, [key])

    def __getattr__(self, name: str) -> JinjaManifestEntry:
        """Get a manifest entry."""
        return JinjaManifestEntry(name, [name])


class MockManifestLoader(JinjaManifestLoader):
    """Manifest loader creating a mocked manifest."""

    @override
    def load(self, filepath: str) -> MockJinjaManifest:
        """Load the manifest."""
        return MockJinjaManifest()
