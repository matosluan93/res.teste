import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User, UserRole

@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()

@pytest.fixture
def recruiter_user(db):
    user = User(name="Test Recruiter", email="recruiter@test.com", role=UserRole.RECRUITER, is_active=True)
    user.set_password("Test@1234")
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def auth_headers(client, recruiter_user):
    resp = client.post("/api/auth/login", json={"email":"recruiter@test.com","password":"Test@1234"})
    token = resp.json["access_token"]
    return {"Authorization": f"Bearer {token}"}
