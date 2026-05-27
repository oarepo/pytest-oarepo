#
# Copyright (c) 2026 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
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
def resourcetypes_rt(app, db) -> VocabularyType:  # noqa
    existing = db.session.query(VocabularyType).filter_by(id="resourcetypes").first()
    if existing:
        return existing
    vt = VocabularyType(id="resourcetypes", pid_type="v-rt")  # type: ignore[reportCallIssue]
    db.session.add(vt)
    db.session.commit()
    return vt


@pytest.fixture
def resourcetype_dataset(app, db, resourcetypes_rt) -> Vocabulary:  # noqa
    try:
        return cast(
            "Vocabulary",
            record_from_result(
                current_service.read(
                    system_identity,
                    ("resourcetypes", "dataset"),  # type: ignore[reportArgumentType]
                )
            ),
        )
    except:  # noqa E722
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
