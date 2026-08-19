from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.role import Role
from mappers.role_mapper import roles_to_schema


async def get_all_roles(
    db: AsyncSession
):

    result = await db.execute(
        select(Role)
    )

    roles = result.scalars().all()

    return roles_to_schema(roles)