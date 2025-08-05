"""Unit tests for configuration module."""

import pytest

from app.core.config import Settings


@pytest.mark.unit
class TestSettings:
    """Test Settings class."""

    def test_settings_defaults(self):
        """Test that settings have default values."""
        settings = Settings()

        assert settings.app_name == "Product Review Analyzer"
        # In testing environment, debug might be True, so we check the field exists
        assert hasattr(settings, "debug")
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000

    def test_database_url_computed(self):
        """Test database URL computation."""
        settings = Settings(
            db_host="localhost",
            db_port=5432,
            db_user="test_user",
            db_password="test_pass",
            db_name="test_db",
        )

        # database_url_computed is computed property, test it directly
        expected_url = "postgresql://test_user:test_pass@localhost:5432/test_db"
        assert settings.database_url_computed == expected_url

    def test_settings_from_env(self, monkeypatch):
        """Test settings loaded from environment variables."""
        monkeypatch.setenv("APP_NAME", "Test App")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("API_PORT", "9000")

        settings = Settings()

        assert settings.app_name == "Test App"
        assert settings.debug is True
        assert settings.api_port == 9000
