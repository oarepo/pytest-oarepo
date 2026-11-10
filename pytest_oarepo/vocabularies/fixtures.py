# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Vocabulary fixtures."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service
from invenio_vocabularies.records.models import VocabularyType
from oarepo_runtime.typing import record_from_result

if TYPE_CHECKING:
    from invenio_vocabularies.records.api import Vocabulary


@pytest.fixture
def resourcetypes_rt(app, db) -> VocabularyType:
    existing = db.session.query(VocabularyType).filter_by(id="resourcetypes").first()
    if existing:
        return existing
    vt = VocabularyType(id="resourcetypes", pid_type="v-rt")  # ty: ignore[unknown-argument]
    db.session.add(vt)
    db.session.commit()
    return vt


@pytest.fixture
def resourcetype_dataset(app, db, resourcetypes_rt) -> Vocabulary:
    try:
        return cast(
            "Vocabulary",
            record_from_result(
                current_service.read(
                    system_identity,  # our typing issue
                    ("resourcetypes", "dataset"),  # ty: ignore[invalid-argument-type]
                )
            ),
        )
    except:
        return cast(
            "Vocabulary",
            record_from_result(
                current_service.create(
                    system_identity,
                    {
                        "type": "resourcetypes",
                        "id": "dataset",
                        "title": {"en": "Dataset"},
                    },
                )
            ),
        )
