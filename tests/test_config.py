"""Unit test for project configuration and path resolutions."""

from pathlib import Path

from src.config import PROJECT_ROOT, settings


def test_project_root_exists():
    assert PROJECT_ROOT.exists()
    assert (PROJECT_ROOT / "src").is_dir()
    assert (PROJECT_ROOT / "data").is_dir()


def test_settings_defaults():
    assert settings.APP_ENV in ["development", "production", "test"]
    assert settings.API_PORT == 8000
    assert settings.HF_DATASET_ID == "ManikaSaini/zomato-restaurant-recommendation"
    assert isinstance(settings.RAW_DATA_PATH, Path)
    assert isinstance(settings.PROCESSED_DATA_PATH, Path)
