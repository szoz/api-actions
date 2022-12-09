from os import environ
from time import time

from pytest import fixture

from fastapi.testclient import TestClient

from jwt import decode

from main import app


@fixture
def client() -> TestClient:
    """Create a common test client."""
    return TestClient(app)


@fixture
def user_credentials() -> tuple[str, str]:
    """Return valid users credentials from environment variables"""
    return environ['USER_NAME'], environ['USER_PASSWORD']


@fixture
def token_params() -> dict:
    """Return secret key used to create token."""
    return {'JWT_SECRET': environ['JWT_SECRET'],
            'JWT_ALGORITHM': 'HS256',
            'JWT_EXPIRE': 15 * 60}


@fixture
def user_token(client, user_credentials) -> str:
    """Return valid access token."""
    response = client.post('/login', auth=user_credentials)

    return response.json()['access_token']


def test_root(client):
    """Root endpoint returns 200 response and JSON with status confirmation."""
    response = client.get('/')

    assert response.status_code == 200
    assert response.json() == {'status': 'OK'}


def test_login(client, user_credentials):
    """Login endpoint checks if provided basic auth credentials are valid and returns success or error response."""
    response_no_credentials = client.post('/login')
    response_wrong_password = client.post('/login', auth=(user_credentials[0], 'wrong_password'))
    response_wrong_user = client.post('/login', auth=('wrong_user', 'wrong_password'))

    response_success = client.post('/login', auth=user_credentials)
    payload_success = response_success.json()

    assert response_no_credentials.status_code == 401
    assert response_wrong_password.status_code == 401
    assert response_wrong_user.status_code == 401

    assert response_success.status_code == 200
    assert type(payload_success) == dict
    assert type(payload_success['access_token']) == str


def test_login_jwt(client, user_credentials, token_params):
    """Login response returns JSON with valid JWT token and expiration time."""
    payload = client.post('/login', auth=user_credentials).json()
    token = payload['access_token']
    user = decode(token, options={'verify_signature': False})['user']
    expire = decode(token, options={'verify_signature': False})['exp']

    assert user == user_credentials[0]
    assert payload['expires_in'] == token_params['JWT_EXPIRE']
    assert round(expire - token_params['JWT_EXPIRE']) == round(time())
    assert decode(token, token_params['JWT_SECRET'], algorithms='HS256')  # validate signature


def test_products_auth(client, user_token):
    """Product endpoint requires valid JWT token provided."""
    response_no_token = client.get('/products')
    response_wrong_token = client.get('/products', headers={'Authorization': 'Bearer WRONGTOKEN'})
    response_success = client.get('/products', headers={'Authorization': f'Bearer {user_token}'})

    assert response_no_token.status_code == 403
    assert response_wrong_token.status_code == 401
    assert response_success.status_code == 200


def test_products_response(client, user_token):
    """Products endpoint returns list of all available products."""
    response = client.get('/products', headers={'Authorization': f'Bearer {user_token}'})
    products = response.json()

    assert response.status_code == 200
    assert type(products) == list
    assert 'id' in products[0].keys()
    assert 'name' in products[0].keys()
    assert 'price' in products[0].keys()
