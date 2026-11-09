# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""UI fixtures for pytest-oarepo."""

from __future__ import annotations

from typing import Any

import pytest

from .classes import MockManifestLoader


@pytest.fixture(scope="module")
def app_config(app_config: dict[str, Any]) -> dict[str, Any]:
    """Override pytest-invenio app_config fixture with custom test settings."""
    # Misc / frontend
    app_config.update(
        IIIF_FORMATS=["jpg", "png"],
        APP_RDM_RECORD_THUMBNAIL_SIZES=[500],
        WEBPACKEXT_MANIFEST_LOADER=MockManifestLoader,
    )

    return app_config
