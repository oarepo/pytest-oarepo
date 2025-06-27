from invenio_records_permissions.generators import AnyUser, SystemProcess
from oarepo_runtime.services.config.permissions_presets import EveryonePermissionPolicy
from oarepo_vocabularies.services.permissions import NonDangerousVocabularyOperation
from oarepo_vocabularies.services.config import VocabulariesConfig


class FineGrainedPermissionPolicy(EveryonePermissionPolicy):
    can_create_removalreasons = [SystemProcess(), AnyUser()]
    can_update_removalreasons = [SystemProcess(), NonDangerousVocabularyOperation(AnyUser())]
    can_delete_removalreasons = [SystemProcess(), AnyUser()]

VOCABULARIES_TEST_CONFIG = {
    "VOCABULARIES_PERMISSIONS_PRESETS": ["fine-grained"],
    "OAREPO_PERMISSIONS_PRESETS": {
            "fine-grained": FineGrainedPermissionPolicy
        },
    "VOCABULARIES_SERVICE_CONFIG": VocabulariesConfig,
    }