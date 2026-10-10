from unittest.mock import patch

from app.app import app


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "healthy"}


def test_home():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.data == b"Hello from ADB DevOps Assignment!"


@patch("app.app.psycopg.connect")
def test_db_health(mock_connect):
    mock_connection = mock_connect.return_value.__enter__.return_value
    mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.return_value = (1,)

    client = app.test_client()
    response = client.get("/db-health")

    assert response.status_code == 200
    assert response.json == {"database": "connected"}
    mock_cursor.execute.assert_called_once_with("SELECT 1")
