import pytest
from pytest_oarepo.functions import _index_users


@pytest.fixture()
def users(app, db, UserFixture):
    """
    Predefined user fixtures.
    """
    user1 = UserFixture(
        email="user1@example.org",
        password="password", # NOSONAR
        active=True,
        confirmed=True,
        user_profile={
            "full_name": "user 1",
            "affiliations": "cesnet",
        },
        preferences={
            "locale": "en"
        }
    )
    user1.create(app, db)

    user2 = UserFixture(
        email="user2@example.org",
        password="beetlesmasher", # NOSONAR
        username="beetlesmasher",
        active=True,
        confirmed=True,
        user_profile={
            "full_name": "beetlesmasher",
            "affiliations": "CERN",
        },
        preferences={
            "locale": "en"
        }
    )
    user2.create(app, db)

    user3 = UserFixture(
        email="user3@example.org",
        password="beetlesmasher",  # NOSONAR
        username="beetlesmasherXXL",
        user_profile={
            "full_name": "Maxipes Fik",
            "affiliations": "cesnet",
        },
        preferences={
            "locale": "cs"
        },
        active=True,
        confirmed=True,
    )
    user3.create(app, db)

    user4 = UserFixture(
        email="user4@example.org",
        password="african",  # NOSONAR
        username="african",
        preferences={
            "timezone": "Africa/Dakar"  # something without daylight saving time; +0.0
        },
        active=True,
        confirmed=True,
    )
    user4.create(app, db)

    user5 = UserFixture(
        email="user5@example.org",
        password="mexican",  # NOSONAR
        username="mexican",
        preferences={
            "timezone": "America/Mexico_City"  # something without daylight saving time
        },
        active=True,
        confirmed=True,
    )
    user5.create(app, db)


    user6 = UserFixture(
        email="user6@example.org",
        password="password",  # NOSONAR
        active=True,
        confirmed=True,
    )
    user6.create(app, db)

    user7 = UserFixture(
        email="user7@example.org",
        password="password",  # NOSONAR
        active=True,
        confirmed=True,
    )
    user7.create(app, db)

    user10 = UserFixture(
        email="user10@example.org",
        password="password",  # NOSONAR
        active=True,
        confirmed=True,
    )
    user10.create(app, db)

    db.session.commit()
    _index_users()
    return [user1, user2, user3, user4, user5, user6, user7, user10]