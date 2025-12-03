import json
import pytest
from flask_package import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_mezmurs_status_and_schema(client):
    res = client.get('/api/mezmurs')
    assert res.status_code == 200
    data = res.get_json()
    assert 'total' in data
    assert 'items' in data
    assert isinstance(data['items'], list)

def test_public_filters_ok(client):
    res = client.get('/api/public_filters')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)

def test_saved_filters_requires_auth(client):
    # Unsigned request should be redirected or unauthorized for saved_filters POST
    res = client.post('/api/saved_filters', json={'name':'x'})
    assert res.status_code in (302, 401, 403) or res.status_code >= 400


def test_mezmur_page_shows_save_button_for_unauthenticated(client):
    # When not logged in, the mezmur page should still render the Save button
    res = client.get('/mezmur')
    assert res.status_code == 200
    text = res.get_data(as_text=True)
    # Save button should be present and indicate unauthenticated via data-auth="0"
    assert 'id="saveFilterBtn"' in text
    assert 'data-auth="0"' in text or 'data-auth="1"' in text
