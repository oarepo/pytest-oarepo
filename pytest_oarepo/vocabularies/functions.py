from pathlib import Path
from oarepo_runtime.datastreams import StreamBatch
from oarepo_runtime.datastreams.fixtures import FixturesCallback, load_fixtures
from invenio_records_permissions.generators import AnyUser, SystemProcess
from oarepo_runtime.services.config.permissions_presets import EveryonePermissionPolicy
from oarepo_vocabularies.services.permissions import NonDangerousVocabularyOperation
from oarepo_vocabularies.services.config import VocabulariesConfig


def load_test_vocabularies():
    class ErrCallback(FixturesCallback):
        def batch_finished(self, batch: StreamBatch):
            if batch.failed_entries:
                print(batch.failed_entries)
            super().batch_finished(batch)

    callback = ErrCallback()
    load_fixtures(
        Path(__file__).parent.parent / "vocabularies/data/vocabularies",
        callback=callback,
        system_fixtures=False
    )

class FineGrainedPermissionPolicy(EveryonePermissionPolicy):
    can_create_removalreasons = [SystemProcess(), AnyUser()]
    can_update_removalreasons = [SystemProcess(), NonDangerousVocabularyOperation(AnyUser())]
    can_delete_removalreasons = [SystemProcess(), AnyUser()]

def test_permissions_config():
    return {
    "VOCABULARIES_PERMISSIONS_PRESETS": ["fine-grained"],
    "OAREPO_PERMISSIONS_PRESETS": {
            "fine-grained": FineGrainedPermissionPolicy
        },
    "VOCABULARIES_SERVICE_CONFIG": VocabulariesConfig,
    }