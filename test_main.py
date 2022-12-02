from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    """Root endpoint returns 200 response and JSON with status confirmation."""
    response = client.get('/')

    assert response.status_code == 200
    assert response.json() == {'status': 'OK'}
