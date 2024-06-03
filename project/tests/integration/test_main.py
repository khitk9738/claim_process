def test_hello(client):
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"ping": "hello!"}

def test_prometheus_metrics(client):
    response = client.get("/metrics")

    # assert some metrics are returned
    assert response.status_code == 200
    assert isinstance(response.text, str)
    assert len(response.text) > 0

def test_get_top_provider(client):
    response = client.get("/top_provider")
    assert response.status_code == 404
