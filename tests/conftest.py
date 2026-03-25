import os

import pytest


@pytest.fixture(autouse=True)
def _set_test_env():
    os.environ.setdefault("MODE", "TEST")
    os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/tagflow_test")
    os.environ.setdefault("WB_API_TOKEN", "test_wb_token")
    os.environ.setdefault("OZON_CLIENT_ID", "test_ozon_id")
    os.environ.setdefault("OZON_API_KEY", "test_ozon_key")
    os.environ.setdefault("YM_API_TOKEN", "test_ym_token")
    os.environ.setdefault("YM_BUSINESS_ID", "test_ym_business")
