from pytest import fixture
from fastapi.testclient import TestClient

from main import app


@fixture
def client():
    """Create a common test client."""
    return TestClient(app)


def test_root(client):
    """Root endpoint returns 200 response and JSON with status confirmation."""
    response = client.get('/')

    assert response.status_code == 200
    assert response.json() == {'status': 'OK'}
