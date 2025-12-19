# app/services/hiring_manager_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.hiring_manager import HiringManager
from app.schemas.hiring_manager import Person
import uuid


async def upsert_hiring_manager(db: AsyncSession, person: Person, source_url: str):
    """
    Insert or update hiring manager entry based on (name + company).
    """

    # Check existing by name + company
    existing_query = await db.execute(
        select(HiringManager).where(
            HiringManager.name.ilike(person.name),
            HiringManager.company.ilike(person.company or "")
        )
    )
    existing = existing_query.scalars().first()

    if existing:
        # Update fields that may change
        existing.title = person.title
        existing.location = person.location
        existing.source_url = source_url

        await db.commit()
        await db.refresh(existing)
        return existing

    # Create new entry
    new_entry = HiringManager(
        id=str(uuid.uuid4()),
        name=person.name,
        title=person.title,
        company=person.company,
        location=person.location,
        source_url=source_url,
        email=None,
        email_pattern=None,
        email_confidence=None,
        email_attempts=0,
        last_emailed_at=None
    )

    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)
    return new_entry
