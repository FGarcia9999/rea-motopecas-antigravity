"""Gates funcionais e de segurança de um MVP transacional sem PII."""
import uuid


def order(client, items, key=None):
    return client.post("/api/orders", json={"items": items}, headers={"Idempotency-Key":key or str(uuid.uuid4())})


def test_home_and_headers(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Rota 2 Motopeças" in r.text
    assert "script-src 'self'" in r.headers["Content-Security-Policy"]
    assert r.headers["X-Frame-Options"] == "DENY"
    assert "text/html" in r.headers["content-type"]


def test_health_and_catalogue(client):
    assert client.get("/api/health").json() == {"status":"ok","mode":"demo","payments":False}
    products = client.get("/api/products").json()
    assert len(products) == 12
    assert all(p["stock"] >= 0 and p["price_cents"] > 0 for p in products)
    assert len(client.get("/api/categories").json()) == 6


def test_search_and_category(client):
    assert all("filtro" in p["name"].lower() for p in client.get("/api/products?q=filtro").json())
    assert all(p["category"] == "Freios" for p in client.get("/api/products?category=Freios").json())
    assert client.get("/api/products?q=notfoundname").json() == []


def test_parameterized_query_not_injection(client):
    assert client.get("/api/products", params={"q":"' OR 1=1 --"}).json() == []
    assert client.get("/api/products", params={"q":"%"}).json() == []


def test_bike_compatibility_filter(client):
    r = client.get("/api/products?bike=honda-cg-160&year=2022")
    assert r.status_code == 200
    assert r.json() and all("honda-cg-160" in x["bikes"] for x in r.json())
    assert client.get("/api/products?bike=honda-cg-160&year=2010").json() == []
    assert client.get("/api/products?year=2022").status_code == 422
    assert client.get("/api/products?bike=unknown").status_code == 422


def test_product_details_and_404(client):
    assert client.get("/api/products/1").json()["sku"] == "R2-FR-001"
    assert client.get("/api/products/7777").status_code == 404


def test_order_total_server_side_and_inventory(client):
    p = client.get("/api/products/1").json()
    r = order(client, [{"product_id":1,"quantity":2}])
    assert r.status_code == 201, r.text
    assert r.json()["payment_processed"] is False
    assert r.json()["total_cents"] == 2*p["price_cents"]
    assert r.json()["status"] == "SIMULADO"
    assert client.get("/api/products/1").json()["stock"] == p["stock"]-2
    assert client.get("/api/metrics").json()["demo_orders"] == 1


def test_order_atomic_rollback_on_stock_failure(client):
    before = client.get("/api/products/1").json()["stock"]
    response = order(client,[{"product_id":1,"quantity":1},{"product_id":2,"quantity":10}])
    # Produto 2 tem 18 un. Alteramos para forçar indisponibilidade.
    assert response.status_code == 201
    again = order(client,[{"product_id":1,"quantity":1},{"product_id":12,"quantity":10}])
    assert again.status_code == 409
    assert client.get("/api/products/1").json()["stock"] == before-1
    assert client.get("/api/metrics").json()["demo_orders"] == 1


def test_idempotency_replays_without_double_debit(client):
    key = str(uuid.uuid4())
    body = [{"product_id":3,"quantity":2}]
    first = order(client,body,key)
    stock = client.get("/api/products/3").json()["stock"]
    replay = order(client,body,key)
    assert first.status_code == replay.status_code == 201
    assert replay.json()["replayed"] is True
    assert replay.json()["order_id"] == first.json()["order_id"]
    assert client.get("/api/products/3").json()["stock"] == stock
    assert order(client,[{"product_id":3,"quantity":1}],key).status_code == 409


def test_reject_bad_payloads(client):
    assert order(client,[{"product_id":1,"quantity":0}]).status_code == 422
    assert order(client,[{"product_id":1,"quantity":11}]).status_code == 422
    assert order(client,[{"product_id":1,"quantity":1},{"product_id":1,"quantity":1}]).status_code == 422
    assert order(client,[]).status_code == 422
    assert order(client,[{"product_id":900,"quantity":1}]).status_code == 404
    assert client.post('/api/orders',json={'items':[{'product_id':1,'quantity':1}]}).status_code == 422


def test_reject_invalid_idempotency_key(client):
    assert order(client,[{"product_id":1,"quantity":1}],key='bad key!').status_code == 400


def test_no_personal_customer_fields_in_orders(client):
    r = order(client,[{"product_id":1,"quantity":1}])
    assert r.status_code == 201
    assert set(r.json().keys()) == {"order_id","total_cents","status","payment_processed","replayed"}


def test_client_cannot_supply_unit_price(client):
    r = client.post(
        "/api/orders",
        json={"items": [{"product_id": 1, "quantity": 1, "price_cents": 1}]},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert r.status_code == 422
    assert client.get("/api/metrics").json()["demo_orders"] == 0
