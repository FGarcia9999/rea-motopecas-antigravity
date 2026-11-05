"""Contrato reforçado RF-03: evitar PASS vacuamente verdadeiro em listas vazias."""


def test_rf03_valid_category_not_empty(client):
    response = client.get("/api/products", params={"category": "Freios"})
    assert response.status_code == 200
    items = response.json()
    assert items, "Filtro de categoria válida não pode ser certificado com resultado vazio"
    assert all(item["category"] == "Freios" for item in items)


def test_rf03_unknown_category_empty_but_ok(client):
    response = client.get("/api/products", params={"category": "categoria-inexistente"})
    assert response.status_code == 200
    assert response.json() == []


def test_rf03_empty_category_returns_catalog(client):
    all_items = client.get("/api/products")
    empty_category = client.get("/api/products", params={"category": ""})
    assert all_items.status_code == empty_category.status_code == 200
    assert len(all_items.json()) == 12
    assert empty_category.json() == all_items.json()


def test_rf03_combined_query_and_order(client):
    response = client.get("/api/products", params={"q": "freio", "category": "Freios"})
    assert response.status_code == 200
    items = response.json()
    assert items
    assert all("freio" in x["name"].lower() and x["category"] == "Freios" for x in items)
    assert [x["id"] for x in items] == sorted(x["id"] for x in items)


def test_rf03_no_fake_capacetes_category(client):
    categories = client.get("/api/categories").json()
    assert "Freios" in categories
    assert "capacetes" not in [c.lower() for c in categories]
    r = client.get("/api/products", params={"category": "capacetes"})
    assert r.status_code == 200 and r.json() == []


def test_rf03_combination_with_bike(client):
    response = client.get("/api/products", params={"category": "Freios", "bike": "honda-cg-160"})
    assert response.status_code == 200
    items = response.json()
    assert items
    assert all(x["category"] == "Freios" and "honda-cg-160" in x["bikes"] for x in items)


def test_rf03_invalid_input_length(client):
    assert client.get("/api/products", params={"category": "x" * 41}).status_code == 422
