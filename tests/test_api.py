def test_create_and_get_note(client):
    resp = client.post(
        "/notes",
        json={"title": "Заметка", "content": "какой-то текст про архитектуру", "url": None},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["possible_duplicates"] == []
    note_id = body["note"]["id"]

    resp = client.get(f"/notes/{note_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Заметка"


def test_create_note_reports_duplicate(client):
    client.post("/notes", json={"title": "Про Docker", "content": "docker compose, volumes, networks"})
    resp = client.post(
        "/notes", json={"title": "Про Docker (2)", "content": "docker compose, volumes и networks"}
    )
    assert resp.json()["possible_duplicates"]


def test_search_endpoint(client):
    client.post("/notes", json={"title": "Рецепт борща", "content": "свекла капуста картофель"})
    client.post("/notes", json={"title": "Настройка CI", "content": "github actions pytest"})

    resp = client.get("/search", params={"q": "борщ свекла"})
    assert resp.status_code == 200
    results = resp.json()
    assert results
    assert results[0]["note"]["title"] == "Рецепт борща"


def test_delete_note(client):
    created = client.post("/notes", json={"title": "Временная", "content": "удалю сейчас"}).json()
    note_id = created["note"]["id"]

    resp = client.delete(f"/notes/{note_id}")
    assert resp.status_code == 204

    resp = client.get(f"/notes/{note_id}")
    assert resp.status_code == 404


def test_note_not_found(client):
    resp = client.get("/notes/9999")
    assert resp.status_code == 404
