def test_admin_endpoint_requires_authentication(client):
    response = client.post("/stars/", json={"name": "Jane Doe"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_stars(client, star_factory):
    star_factory(name="John Doe")
    response = client.get("/stars/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "John Doe"


def test_get_star_returns_404(client):
    response = client.get("/stars/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Star with id 999 not found"


def test_get_payments_requires_authentication(client):
    response = client.get("/payments/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_orders_requires_authentication(client):
    response = client.get("/orders/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_movies(client, movie_factory):
    movie_factory(name="The Matrix")
    response = client.get("/movies/")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "The Matrix"


def test_get_cart_requires_authentication(client):
    response = client.get("/carts/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
