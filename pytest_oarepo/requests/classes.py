from flask_principal import UserNeed
from invenio_records_permissions.generators import Generator
from invenio_requests.customizations import CommentEventType
from oarepo_workflows.requests.generators import RecipientGeneratorMixin


class TestEventType(CommentEventType):
    """
    Custom EventType.
    """
    type_id = "test"


class UserGenerator(RecipientGeneratorMixin, Generator):
    """
    Generator primarily used to define specific user as recipient of a request.
    """
    def __init__(self, user_id):
        self.user_id = user_id

    def needs(self, **kwargs):
        return [UserNeed(self.user_id)]

    def reference_receivers(self, **kwargs):
        return [{"user": str(self.user_id)}]
