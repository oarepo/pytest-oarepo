import pytest
from flask_security import login_user
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_api


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return create_api

@pytest.fixture()
def host():
    return "https://127.0.0.1:5000/" #overwritable in application

@pytest.fixture()
def vocab_cf(app, db, cache):
    from oarepo_runtime.services.custom_fields.mappings import prepare_cf_indices

    prepare_cf_indices()

class LoggedClient:
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
