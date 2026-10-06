def test_project_speaks_french_and_knows_the_contact_recipient():
    from django.conf import settings

    assert settings.LANGUAGE_CODE == "fr-fr"
    assert settings.TIME_ZONE == "Europe/Paris"
    assert settings.CONTACT_RECIPIENT_EMAIL == "hellotoutous@hotmail.com"
