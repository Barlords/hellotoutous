def test_database_url_selects_postgresql():
    from config.settings import database_from_url

    config = database_from_url(
        "postgres://toutous:secret@db.example:5432/hellotoutous?sslmode=require"
    )

    assert config["ENGINE"] == "django.db.backends.postgresql"
    assert config["NAME"] == "hellotoutous"
    assert config["USER"] == "toutous"
    assert config["PASSWORD"] == "secret"
    assert config["HOST"] == "db.example"
    assert config["PORT"] == 5432
    assert config["CONN_MAX_AGE"] == 600
    assert config["CONN_HEALTH_CHECKS"] is True
    assert config["OPTIONS"]["sslmode"] == "require"


def test_test_suite_stays_on_sqlite():
    from django.conf import settings

    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"


def test_project_speaks_french_and_knows_the_contact_recipient():
    from django.conf import settings

    assert settings.LANGUAGE_CODE == "fr-fr"
    assert settings.TIME_ZONE == "Europe/Paris"
    assert settings.CONTACT_RECIPIENT_EMAIL == "hellotoutous@barlords.fr"
    assert settings.DEFAULT_FROM_EMAIL == "hellotoutous@barlords.fr"
    assert settings.EMAIL_HOST == "ssl0.ovh.net"
    assert settings.EMAIL_PORT == 587
    assert settings.EMAIL_HOST_USER == "hellotoutous@barlords.fr"
    assert settings.EMAIL_USE_TLS is True
