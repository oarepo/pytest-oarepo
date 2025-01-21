import pytest
from flask_security import login_user
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_api
import copy

from deepmerge import always_merger

@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return create_api

@pytest.fixture()
def host():
    return "https://127.0.0.1:5000/"

@pytest.fixture()
def link2testclient(host):
    def _link2testclient(link, ui=False):
        base_string = f"{host}api/" if not ui else host
        return link[len(base_string) - 1 :]
    return _link2testclient

@pytest.fixture()
def default_record_json():
    """
    Default data for creating a record, without default workflow.
    """
    return {
        "metadata": {
            "creators": [
                "Creator 1",
                "Creator 2",
            ],
            "contributors": ["Contributor 1"],
            "title": "blabla",
        },
        "files": {"enabled": False},
    }


@pytest.fixture()
def default_record_with_workflow_json(default_record_json):
    """
    Default data for creating a record.
    """
    return {
        **default_record_json,
        "parent": {"workflow": "default"},
    }

@pytest.fixture()
def prepare_record_data(default_record_json):
    """
    Function for merging input definitions into data passed to record service.
    """
    def _merge_record_data(
        custom_data=None, custom_workflow=None, additional_data=None, add_default_workflow=True
    ):
        """
        :param custom_workflow: If user wants to use different workflow that the default one.
        :param additional_data: Additional data beyond the defaults that should be put into the service.
        :param add_default_workflow: Allows user to to pass data into the service without workflow - this might be useful for example
        in case of wanting to use community default workflow.
        """
        record_json = (
            default_record_json if not custom_data else custom_data
        )
        json = copy.deepcopy(record_json)
        if add_default_workflow:
            always_merger.merge(json, {"parent": {"workflow": "default"}})
        if custom_workflow:  # specifying this assumes use of workflows
            json.setdefault("parent", {})["workflow"] = custom_workflow
        if additional_data:
            always_merger.merge(json, additional_data)

        return json
    return _merge_record_data

@pytest.fixture()
def vocab_cf(app, db, cache):
    from oarepo_runtime.services.custom_fields.mappings import prepare_cf_indices

    prepare_cf_indices()


class LoggedClient:
    # todo - using the different clients thing?
    def __init__(self, client, user_fixture):
        self.client = client
        self.user_fixture = user_fixture

    def _login(self):
        login_user(self.user_fixture.user, remember=True)
        login_user_via_session(self.client, email=self.user_fixture.email)

    def post(self, *args, **kwargs):
        self._login()
        return self.client.post(*args, **kwargs)

    def get(self, *args, **kwargs):
        self._login()
        return self.client.get(*args, **kwargs)

    def put(self, *args, **kwargs):
        self._login()
        return self.client.put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._login()
        return self.client.delete(*args, **kwargs)


@pytest.fixture()
def logged_client(client):
    def _logged_client(user):
        return LoggedClient(client, user)

    return _logged_client
