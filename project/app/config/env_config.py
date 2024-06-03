import os
from dotenv import load_dotenv
from dotmap import DotMap

load_dotenv()

envs = {
    "APP_NAME": os.getenv("APP_NAME", "APPLICATION_NAME"),
    "ENVIRONMENT": os.getenv("ENVIRONMENT", "local"),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    "DATABASE_URL": os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/foo"),
}


def validate_envs(envs) -> None:
    """
    The function `validate_envs` checks if all environment variables are set and raises a `RuntimeError`
    listing the missing ones if any are found.
    
    :param envs: The `validate_envs` function takes a dictionary `envs` as input, where the keys are
    environment variable names and the values are the corresponding values of those environment
    variables. The function checks if any of the environment variables have a value of `None` or an
    empty string `""`. If
    """
    """Validate that all environment variables are set."""
    missing_envs = [k for k, v in envs.items() if v in [None, ""]]
    if missing_envs:
        raise RuntimeError(
            f"The following environment variables are not set:\n{missing_envs}"
        )


validate_envs(envs)
envs = DotMap(envs)
