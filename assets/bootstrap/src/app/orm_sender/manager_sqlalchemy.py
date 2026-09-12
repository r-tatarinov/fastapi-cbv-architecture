from sqlalchemy.ext.asyncio import create_async_engine

from src.app.config import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_TIMEZONE,
    DATABASE_USER,
)


class ManagerSQLAlchemy:

    engine = create_async_engine(
        f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}",
        connect_args={"server_settings": {"timezone": DATABASE_TIMEZONE}},
    )
