import pytest

from pytest_oarepo.functions import _index_users


@pytest.fixture()
def users(app, db, UserFixture):
    # todo use en locales? i'm not completely sure it won't break something
    """
    Predefined user fixtures.
    """
    user1 = UserFixture(
        email="user1@example.org",
        password="password",
        active=True,
        confirmed=True,
        user_profile={
            "affiliations": "CERN",
        },
    )
    user1.create(app, db)

    user2 = UserFixture(
        email="user2@example.org",
        password="beetlesmasher",
        username="beetlesmasher",
        active=True,
        confirmed=True,
        user_profile={
            "affiliations": "CERN",
        },
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
            "timezone": "Africa/Dakar",  # something without daylight saving time; +0.0
        },
        user_profile={
            "affiliations": "CERN",
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
            "timezone": "America/Mexico_City",  # something without daylight saving time
        },
        user_profile={
            "affiliations": "CERN",
        },
        active=True,
        confirmed=True,
    )
    user5.create(app, db)

    db.session.commit()
    _index_users()
    return [user1, user2, user3, user4, user5]


@pytest.fixture()
def user_with_cs_locale(
    app, db, users, UserFixture
):  # adding to users would cause backward compatibility issues; problem - can't enforce consistent id once more users added to users
    u = UserFixture(
        email="pat@mat.cz",
        password="patmat",  # NOSONAR
        username="patmat",
        user_profile={
            "full_name": "patmat",
            "affiliations": "cesnet",
        },
        preferences={"locale": "cs"},
        active=True,
        confirmed=True,
    )
    u.create(app, db)
    db.session.commit()
    _index_users()
    return u
