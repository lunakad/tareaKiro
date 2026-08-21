"""
Property-based integration tests for Usuario.

Validates: Requirements 5.1, 5.2, 5.4, 6.1, 6.3, 7.1, 7.5, 9.5

Properties covered:
  - Property 9:  Password never exposed in any Usuario response
  - Property 10: Stored password hash is verifiable with bcrypt
  - Property 12: Username uniqueness on creation
  - Property 13: One Usuario per Persona (1:1 relationship)
  - Property 14: Round-trip create/read of Usuario (without password)
"""

import json
import bcrypt
import pytest
from unittest.mock import patch
from hypothesis import given, settings, strategies as st
from app import create_app, db as _db


# ---------------------------------------------------------------------------
# App factory for Hypothesis (fresh in-memory DB per example)
# ---------------------------------------------------------------------------

def make_app():
    return create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })


# ---------------------------------------------------------------------------
# Strategies
#
# username: alphanumeric ASCII only (3-50 chars) — safe for DB and HTTP
# password: printable ASCII only (8-72 chars) — bcrypt limit is 72 bytes;
#           with ASCII (1 byte/char) this guarantees we never exceed it.
# ---------------------------------------------------------------------------

_alnum = st.characters(whitelist_categories=("Lu", "Ll", "Nd"),
                       whitelist_characters="",
                       blacklist_characters="")

username_st = st.from_regex(r"[A-Za-z0-9]{3,50}", fullmatch=True)
password_st = st.from_regex(r"[A-Za-z0-9!@#$%^&*_\-]{8,72}", fullmatch=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _post_json(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type="application/json")


def _put_json(client, url, payload):
    return client.put(url, data=json.dumps(payload), content_type="application/json")


def _crear_persona(client, doc, email):
    """Create a Persona with explicitly provided unique doc and email."""
    payload = {
        "nombre": "Test",
        "apellido": "User",
        "documento": doc[:20],
        "fecha_nacimiento": "1990-01-01",
        "email": email[:254],
    }
    resp = _post_json(client, "/personas", payload)
    assert resp.status_code == 201, f"Persona creation failed: {resp.get_json()}"
    return resp.get_json()


def _no_password_fields(data: dict) -> bool:
    return "password" not in data and "password_hash" not in data


# ---------------------------------------------------------------------------
# Property 9: Password never exposed in any Usuario response
# Validates: Requirements 5.1, 6.1, 6.3, 7.1
# ---------------------------------------------------------------------------

@given(username=username_st, password=password_st)
@settings(max_examples=50, deadline=None)
def test_property_9_password_never_exposed(username, password):
    """
    For any valid username/password, POST, GET, and PUT responses
    must NOT contain keys 'password' or 'password_hash'.

    **Validates: Requirements 5.1, 6.1, 6.3, 7.1**
    """
    with patch("bcrypt.gensalt", return_value=bcrypt.gensalt(rounds=4)):
        app = make_app()
        with app.app_context():
            _db.create_all()
            client = app.test_client()

            doc = (username + "d")[:20]
            email = f"{username[:30]}@test.com"
            persona = _crear_persona(client, doc=doc, email=email)

            post_resp = _post_json(client, "/usuarios", {
                "persona_id": persona["id"],
                "username": username,
                "password": password,
            })
            assert post_resp.status_code == 201
            post_body = post_resp.get_json()
            assert _no_password_fields(post_body), (
                f"POST response exposed password fields: {list(post_body.keys())}"
            )

            user_id = post_body["id"]

            get_resp = client.get(f"/usuarios/{user_id}")
            assert get_resp.status_code == 200
            get_body = get_resp.get_json()
            assert _no_password_fields(get_body), (
                f"GET response exposed password fields: {list(get_body.keys())}"
            )

            new_username = (username + "x")[:50]
            put_resp = _put_json(client, f"/usuarios/{user_id}", {"username": new_username})
            assert put_resp.status_code == 200
            put_body = put_resp.get_json()
            assert _no_password_fields(put_body), (
                f"PUT response exposed password fields: {list(put_body.keys())}"
            )

            _db.session.remove()
            _db.drop_all()


# ---------------------------------------------------------------------------
# Property 10: Stored password hash is verifiable with bcrypt
# Validates: Requirements 5.1, 7.5
# ---------------------------------------------------------------------------

@given(password=password_st)
@settings(max_examples=50, deadline=None)
def test_property_10_password_hash_verifiable(password):
    """
    For any valid password, after creating a Usuario, bcrypt.checkpw
    against the stored hash must return True.

    **Validates: Requirements 5.1, 7.5**
    """
    with patch("bcrypt.gensalt", return_value=bcrypt.gensalt(rounds=4)):
        app = make_app()
        with app.app_context():
            _db.create_all()
            client = app.test_client()

            safe = "".join(c for c in password[:16] if c.isalnum()) or "x"
            doc = f"doc{safe}"[:20]
            email = f"u{safe[:20]}@test.com"
            persona = _crear_persona(client, doc=doc, email=email)

            username = ("usr" + safe[:10])[:50]
            if len(username) < 3:
                username = "usr"

            post_resp = _post_json(client, "/usuarios", {
                "persona_id": persona["id"],
                "username": username,
                "password": password,
            })
            assert post_resp.status_code == 201, f"Create failed: {post_resp.get_json()}"
            user_id = post_resp.get_json()["id"]

            from usuarios.models import Usuario
            usuario = _db.session.get(Usuario, user_id)
            assert usuario is not None
            assert bcrypt.checkpw(
                password.encode("utf-8"),
                usuario.password_hash.encode("utf-8"),
            ), "bcrypt.checkpw returned False for the stored hash"

            _db.session.remove()
            _db.drop_all()


# ---------------------------------------------------------------------------
# Property 12: Username uniqueness on creation
# Validates: Requirements 5.2, 9.5
# ---------------------------------------------------------------------------

@given(username=username_st, password=password_st)
@settings(max_examples=50, deadline=None)
def test_property_12_username_uniqueness(username, password):
    """
    Two POST /usuarios requests sharing the same username must result in
    HTTP 409 for the second request.

    **Validates: Requirements 5.2, 9.5**
    """
    with patch("bcrypt.gensalt", return_value=bcrypt.gensalt(rounds=4)):
        app = make_app()
        with app.app_context():
            _db.create_all()
            client = app.test_client()

            # Two distinct personas — guaranteed-unique doc/email using "1"/"2" suffix
            doc_a = f"da{username}"[:20]
            doc_b = f"db{username}"[:20]
            email_a = f"a{username[:28]}@test.com"
            email_b = f"b{username[:28]}@test.com"
            persona_a = _crear_persona(client, doc=doc_a, email=email_a)
            persona_b = _crear_persona(client, doc=doc_b, email=email_b)

            first = _post_json(client, "/usuarios", {
                "persona_id": persona_a["id"],
                "username": username,
                "password": password,
            })
            assert first.status_code == 201

            second = _post_json(client, "/usuarios", {
                "persona_id": persona_b["id"],
                "username": username,
                "password": password,
            })
            assert second.status_code == 409, (
                f"Expected 409 for duplicate username '{username}', got {second.status_code}"
            )

            _db.session.remove()
            _db.drop_all()


# ---------------------------------------------------------------------------
# Property 13: One Usuario per Persona (1:1 relationship)
# Validates: Requirement 5.4
# ---------------------------------------------------------------------------

@given(username=username_st, password=password_st)
@settings(max_examples=50, deadline=None)
def test_property_13_one_usuario_per_persona(username, password):
    """
    A second POST /usuarios for a persona_id that already has a Usuario
    must return HTTP 409.

    **Validates: Requirement 5.4**
    """
    username_b = (username + "2")[:50]
    if len(username_b) < 3:
        username_b = "usr" + username_b

    with patch("bcrypt.gensalt", return_value=bcrypt.gensalt(rounds=4)):
        app = make_app()
        with app.app_context():
            _db.create_all()
            client = app.test_client()

            doc = f"dp{username}"[:20]
            email = f"p{username[:28]}@test.com"
            persona = _crear_persona(client, doc=doc, email=email)

            first = _post_json(client, "/usuarios", {
                "persona_id": persona["id"],
                "username": username,
                "password": password,
            })
            assert first.status_code == 201

            second = _post_json(client, "/usuarios", {
                "persona_id": persona["id"],
                "username": username_b,
                "password": password,
            })
            assert second.status_code == 409, (
                f"Expected 409 for second usuario on same persona, got {second.status_code}"
            )

            _db.session.remove()
            _db.drop_all()


# ---------------------------------------------------------------------------
# Property 14: Round-trip create/read of Usuario (without password)
# Validates: Requirements 6.3, 5.1
# ---------------------------------------------------------------------------

@given(username=username_st, password=password_st)
@settings(max_examples=50, deadline=None)
def test_property_14_round_trip_usuario(username, password):
    """
    After a successful POST /usuarios, GET /usuarios/<id> must return
    the same username and persona_id, with no password or password_hash fields.

    **Validates: Requirements 6.3, 5.1**
    """
    with patch("bcrypt.gensalt", return_value=bcrypt.gensalt(rounds=4)):
        app = make_app()
        with app.app_context():
            _db.create_all()
            client = app.test_client()

            doc = f"dr{username}"[:20]
            email = f"r{username[:28]}@test.com"
            persona = _crear_persona(client, doc=doc, email=email)

            post_resp = _post_json(client, "/usuarios", {
                "persona_id": persona["id"],
                "username": username,
                "password": password,
            })
            assert post_resp.status_code == 201
            created = post_resp.get_json()

            get_resp = client.get(f"/usuarios/{created['id']}")
            assert get_resp.status_code == 200
            fetched = get_resp.get_json()

            assert fetched["username"] == username, (
                f"Username mismatch: expected '{username}', got '{fetched['username']}'"
            )
            assert fetched["persona_id"] == persona["id"], (
                f"persona_id mismatch: expected {persona['id']}, got {fetched['persona_id']}"
            )
            assert _no_password_fields(fetched), (
                f"GET /usuarios/<id> exposed password fields: {list(fetched.keys())}"
            )

            _db.session.remove()
            _db.drop_all()
