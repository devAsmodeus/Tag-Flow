from src.infrastructure.config import Settings


def test_settings_loads_from_env():
    settings = Settings()
    assert settings.mode == "TEST"
    assert settings.is_test is True
    assert settings.wb_token == "test_wb_token"
    assert settings.poll_interval_minutes == 30
    assert settings.max_retries == 3


def test_settings_defaults():
    settings = Settings()
    assert settings.ollama_url == "http://localhost:11434"
    assert settings.tagger_model == "qwen3:8b"
    assert settings.responder_model == "qwen3:8b"
    assert settings.log_level == "INFO"
