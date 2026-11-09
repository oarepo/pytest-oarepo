# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

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
