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

    user4 = UserFixture(
        email="user4@example.org",
        password="african",
        username="african",
        preferences={
            "timezone": "Africa/Dakar", # something without daylight saving time; +0.0
        },
        active=True,
        confirmed=True,
    )
    user4.create(app, db)

    user5 = UserFixture(
        email="user5@example.org",
        password="mexican",
        username="mexican",
        preferences={
            "timezone": "America/Mexico_City", # something without daylight saving time
        },
        active=True,
        confirmed=True,
    )
    user5.create(app, db)

    db.session.commit()
    UserAggregate.index.refresh()
    return [user1, user2, user3, user4, user5]