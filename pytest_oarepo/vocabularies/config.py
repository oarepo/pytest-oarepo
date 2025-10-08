#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of pytest-oarepo (see https://github.com/oarepo/pytest_oarepo).
#
# pytest-oarepo is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Vocabularies config module for pytest-oarepo."""

from __future__ import annotations

# TODO: this should have been chnged in new RDM?
"""
class FineGrainedPermissionPolicy(EveryonePermissionPolicy):
    can_create_removalreasons = (SystemProcess(), AnyUser()]
    can_update_removalreasons = [
        SystemProcess(),
        NonDangerousVocabularyOperation(AnyUser()),
    ]
    can_delete_removalreasons = [SystemProcess(), AnyUser()]


VOCABULARIES_TEST_CONFIG = {
    "VOCABULARIES_PERMISSIONS_PRESETS": ["fine-grained"],
    "OAREPO_PERMISSIONS_PRESETS": {"fine-grained": FineGrainedPermissionPolicy},
    "VOCABULARIES_SERVICE_CONFIG": VocabulariesConfig,
}
"""
