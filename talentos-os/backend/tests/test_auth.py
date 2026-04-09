def test_login_success(client, recruiter_user):
    resp = client.post("/api/auth/login", json={"email":"recruiter@test.com","password":"Test@1234"})
    assert resp.status_code == 200
    assert "access_token" in resp.json
    assert "user" in resp.json

def test_login_invalid_password(client, recruiter_user):
    resp = client.post("/api/auth/login", json={"email":"recruiter@test.com","password":"errado"})
    assert resp.status_code == 401

def test_login_missing_fields(client):
    resp = client.post("/api/auth/login", json={"email":"test@test.com"})
    assert resp.status_code == 422

def test_me_endpoint(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json["role"] == "recruiter"

def test_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json["status"] == "ok"
