import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def app():
    from ..app.main import app
    return app

@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def envs():
    from ..app.config.env_config import envs
    return envs


def assert_all_logs_contain_trace_info(caplog, envs):
    for log in caplog.records:
        assert log.otelTraceID is not None
        assert log.otelSpanID is not None
        assert log.otelServiceName == envs.APP_NAME
