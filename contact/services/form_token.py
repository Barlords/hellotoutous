import secrets

TOKEN_KEY = "contact_form_token"


def issue_token(session) -> str:
    token = secrets.token_urlsafe(16)
    session[TOKEN_KEY] = token
    session.modified = True
    return token


def current_token(session) -> str:
    token = session.get(TOKEN_KEY)
    if token:
        return token
    return issue_token(session)


def consume_token(session, posted: str) -> bool:
    expected = session.get(TOKEN_KEY)
    if not posted or posted != expected:
        return False
    session.pop(TOKEN_KEY, None)
    session.modified = True
    return True
