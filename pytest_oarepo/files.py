from io import BytesIO

import pytest


@pytest.fixture()
def file_metadata():
    return {"title": "Test file"}


@pytest.fixture()
def upload_file(file_metadata):
    def _upload_file(
        identity,
        record_id,
        files_service,
        file_name="test.pdf",
        custom_file_metadata=None,
    ):
        """
        Uploads a default file to a record.
        :param identity: Identity of the requester.
        :param record_id: Id of the record to be uploaded on.
        :param files_service: Service to upload the file.
        :param file_name: Name of the file to be uploaded.
        :param custom_file_metadata: Custom metadata to be uploaded.
        """
        actual_file_metadata = (
            file_metadata if not custom_file_metadata else custom_file_metadata
        )
        init = files_service.init_files(
            identity,
            record_id,
            data=[
                {"key": file_name, "metadata": actual_file_metadata},
            ],
        )
        upload = files_service.set_file_content(
            identity, record_id, file_name, stream=BytesIO(b"testfile")
        )
        commit = files_service.commit_file(identity, record_id, file_name)
        return commit

    return _upload_file
