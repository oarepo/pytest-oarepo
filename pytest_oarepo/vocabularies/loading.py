from pathlib import Path

from oarepo_runtime.datastreams import StreamBatch
from oarepo_runtime.datastreams.fixtures import FixturesCallback, load_fixtures


def load_test_vocabularies():
    class ErrCallback(FixturesCallback):
        def batch_finished(self, batch: StreamBatch):
            if batch.failed_entries:
                print(batch.failed_entries)
            super().batch_finished(batch)

    callback = ErrCallback()
    load_fixtures(
        Path(__file__).parent / "data",
        callback=callback,
        system_fixtures=False
    )
