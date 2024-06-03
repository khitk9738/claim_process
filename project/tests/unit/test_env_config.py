import pytest
from project.app.config.env_config import validate_envs

def test_valid_envs():
    envs = { "ENVIRONMENT": "local"}
    # no error should be raised
    validate_envs(envs)

def test_empty_env():
    envs = { "ENVIRONMENT": ""}
    # error should be raised as we have empty environment variables set
    with pytest.raises(RuntimeError):
        validate_envs(envs)

def test_null_env():
    envs = { "ENVIRONMENT": None}
    # error should be raised as we have null environment variables set
    with pytest.raises(RuntimeError):
        validate_envs(envs)
