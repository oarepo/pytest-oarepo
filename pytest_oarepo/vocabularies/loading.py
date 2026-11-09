# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Module for loading vocabulary fixtures."""

from __future__ import annotations

# TODO: datastreams scrapped
"""
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from invenio_vocabularies.records.api import Vocabulary
from oarepo_runtime.datastreams.fixtures import FixturesCallback, load_fixtures

if TYPE_CHECKING:
    from oarepo_runtime.datastreams import StreamBatch


@pytest.fixture
def test_vocabularies() -> None:


    class ErrCallback(FixturesCallback):

        def batch_finished(self, batch: StreamBatch) -> None:
            if batch.failed_entries:
                pass
            super().batch_finished(batch)

    callback = ErrCallback()
    load_fixtures(Path(__file__).parent / "data", callback=callback, system_fixtures=False)
    Vocabulary.index.refresh()
"""
