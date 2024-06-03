import os
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")

# The line `engine = AsyncEngine(create_engine(DATABASE_URL, echo=True, future=True))` is creating an
# asynchronous engine for interacting with the database. Here's what each part of the line is doing:
# - `create_engine(DATABASE_URL, echo=True, future=True)`: This function creates an engine using the
#   `DATABASE_URL` environment variable as the connection string. The `echo=True` parameter enables
#   logging of SQL queries, and the `future=True` parameter enables the use of SQLAlchemy's async
#   capabilities.
engine = AsyncEngine(create_engine(DATABASE_URL, echo=True, future=True))

async def init_db():
    """
    The `init_db` function initializes the database by creating all tables defined in the `SQLModel`
    metadata. The function uses the `create_all` method from the `metadata` attribute of the `SQLModel`
    """
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """
    The function `get_session` returns an asynchronous session using `AsyncSession` class with a context
    manager. The session is created using the `sessionmaker` function from `sqlalchemy.orm` module.
    """
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session