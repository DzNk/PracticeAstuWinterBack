import asyncio
from pathlib import Path

from backend.session import init_db


async def create_database():
    await init_db()
    project_root = Path(__file__).resolve().parent  # Move up to the parent directory
    versions_dir = project_root / "alembic" / "versions"
    if not versions_dir.exists():
        versions_dir.mkdir(parents=True)


if __name__ == "__main__":
    asyncio.run(create_database())
