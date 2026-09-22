import asyncio
import logging
from pathlib import Path

import asyncpg

from app.core.config import settings


MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
logger = logging.getLogger(__name__)


def get_database_url() -> str:
    return settings.asyncpg_database_url


async def run_migrations() -> None:
    connection = await asyncpg.connect(get_database_url())
    try:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )

        applied_rows = await connection.fetch("SELECT filename FROM schema_migrations")
        applied = {row["filename"] for row in applied_rows}
        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

        for migration_file in migration_files:
            if migration_file.name in applied:
                logger.info("Skipping already applied migration %s", migration_file.name)
                continue

            sql = migration_file.read_text(encoding="utf-8")
            async with connection.transaction():
                await connection.execute(sql)
                await connection.execute(
                    "INSERT INTO schema_migrations (filename) VALUES ($1)",
                    migration_file.name,
                )
            logger.info("Applied migration %s", migration_file.name)
    finally:
        await connection.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    asyncio.run(run_migrations())
