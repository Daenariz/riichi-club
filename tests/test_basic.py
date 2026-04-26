import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for tests
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads."""
    rv = client.get('/')
    assert rv.status_code == 200
    # This test assumes 'Riichi Club' is present on your home page.
    # You can adjust this to match your actual content.
    assert b'Riichi Club' in rv.data
