def test_list_candidates_requires_auth(client):
    resp = client.get("/api/candidates/")
    assert resp.status_code == 401

def test_list_candidates_authenticated(client, auth_headers):
    resp = client.get("/api/candidates/", headers=auth_headers)
    assert resp.status_code == 200
    assert "items" in resp.json
    assert "total" in resp.json

def test_create_candidate(client, auth_headers):
    resp = client.post("/api/candidates/", headers=auth_headers, json={
        "name": "João Silva", "email": "joao@test.com",
        "current_role": "Dev", "area": "Tecnologia"
    })
    assert resp.status_code == 201
    assert resp.json["name"] == "João Silva"

def test_create_candidate_missing_name(client, auth_headers):
    resp = client.post("/api/candidates/", headers=auth_headers, json={"email":"x@x.com"})
    assert resp.status_code == 422
