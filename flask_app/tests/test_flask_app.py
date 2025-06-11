import pytest
import asyncio
from unittest.mock import patch, Mock
from flask_app.flask_app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test main page loads"""
    response = client.get('/')
    assert response.status_code == 200

def test_health_endpoint(client):
    """Test health check"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

@patch('flask_app.flask_app.requests.get')
def test_call_tornado_success(mock_get, client):
    """Test successful Tornado call"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "Hello, world"
    mock_get.return_value = mock_response
    
    response = client.post('/call-tornado', data={'endpoint': '/'})
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['response_text'] == "Hello, world"

@patch('flask_app.flask_app.requests.get')
def test_call_tornado_connection_error(mock_get, client):
    """Test Tornado connection failure"""
    mock_get.side_effect = Exception("Connection failed")
    
    response = client.post('/call-tornado', data={'endpoint': '/'})
    assert response.status_code == 500
    assert response.json['success'] is False

def test_call_tornado_async_endpoint_returns_json(client):
    """Test that async endpoint returns valid JSON (fixing the original parsing error)"""
    response = client.post('/call-tornado-async', data={'endpoint': '/'})
    
    # The key test: response should be valid JSON with proper content type
    assert response.content_type == 'application/json'
    
    # Should be able to parse JSON without errors
    json_data = response.json
    assert 'success' in json_data
    
    # Response should be either success (if Tornado is running) or error (if not)
    if json_data['success']:
        assert 'response_text' in json_data
        assert 'status_code' in json_data
    else:
        assert 'error' in json_data