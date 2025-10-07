from functools import cached_property

from flask_principal import UserNeed
from invenio_records_permissions.generators import Generator
from invenio_requests.customizations import CommentEventType
from oarepo_workflows.requests.generators import RecipientGeneratorMixin
from invenio_access.models import User
from invenio_accounts.models import User

class TestEventType(CommentEventType):
    """
    Custom EventType.
    """
    type_id = "T"


class SystemUserGenerator(RecipientGeneratorMixin, Generator):
    """
    Generator primarily used to define system user as recipient of a request.
    """

    def needs(self, **kwargs):
        return [UserNeed("system")]

    def reference_receivers(self, **kwargs):
        return [{"user": "system"}]

class UserGenerator(RecipientGeneratorMixin, Generator):
    """
    Generator primarily used to define specific user as recipient of a request.
    """
    def __init__(self, user_email):
        self.user_email = user_email

    @property
    def user_id(self):
        return User.query.filter_by(email=self.user_email).one().id

    def needs(self, **kwargs):
        return [UserNeed(self.user_id)]

    def reference_receivers(self, **kwargs):
        return [{"user": str(self.user_id)}]



class CSLocaleUserGenerator(RecipientGeneratorMixin, Generator):
    """
    Generator primarily used to define specific user as recipient of a request.
    """
    def _get_user_id(self):
        users = User.query.all()
        users = [user for user in users if "locale" in user.preferences and user.preferences["locale"] == 'cs']
        if users:
            return users[0].id
        else:
            raise ValueError("No CS locale user found")

    def needs(self, **kwargs):
        return [UserNeed(self._get_user_id())]

    def reference_receivers(self, **kwargs):
        return [{"user": str(self._get_user_id())}]