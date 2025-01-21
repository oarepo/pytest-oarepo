import pytest
from invenio_users_resources.records import UserAggregate


@pytest.fixture()
def users(app, db, UserFixture):
    """
    Predefined user fixtures.
    """
    user1 = UserFixture(
        email="user1@example.org",
        password="password",
        active=True,
        confirmed=True,
    )
    user1.create(app, db)

    user2 = UserFixture(
        email="user2@example.org",
        password="beetlesmasher",
        username="beetlesmasher",
        active=True,
        confirmed=True,
    )
    user2.create(app, db)

    user3 = UserFixture(
        email="user3@example.org",
        password="beetlesmasher",
        username="beetlesmasherXXL",
        user_profile={
            "full_name": "Maxipes Fik",
            "affiliations": "CERN",
        },
        active=True,
        confirmed=True,
    )
    user3.create(app, db)

    db.session.commit()
    UserAggregate.index.refresh()
    return [user1, user2, user3]
