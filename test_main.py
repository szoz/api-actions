from os import environ

from pytest import fixture

from fastapi.testclient import TestClient

from main import app


@fixture
def client() -> TestClient:
    """Create a common test client."""
    return TestClient(app)


@fixture
def user_credentials() -> tuple[str, str]:
    """Return valid users credentials from environment variables"""
    return environ['USER_NAME'], environ['USER_PASSWORD']


def test_root(client):
    """Root endpoint returns 200 response and JSON with status confirmation."""
    response = client.get('/')

    assert response.status_code == 200
    assert response.json() == {'status': 'OK'}


def test_products(client):
    """Products endpoint returns list of all available products."""
    response = client.get('/products')
    products = response.json()

    assert response.status_code == 200
    assert type(products) == list
    assert 'id' in products[0].keys()
    assert 'name' in products[0].keys()
    assert 'price' in products[0].keys()


def test_login(client, user_credentials):
    """Login endpoint checks if provided basic auth credentials are valid and returns success or error response."""
    response_success = client.get('/login', auth=user_credentials)
    response_no_credentials = client.get('/login')
    response_wrong_password = client.get('/login', auth=(user_credentials[0], 'wrong_password'))
    response_wrong_user = client.get('/login', auth=('wrong_user', 'wrong_password'))

    assert response_success.status_code == 200
    assert response_no_credentials.status_code == 401
    assert response_wrong_password.status_code == 401
    assert response_wrong_user.status_code == 401
