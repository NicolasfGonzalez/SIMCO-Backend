from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.user import User
from core.security import verify_password

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    # Consultar el usuario en la BD de forma asíncrona
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    # Si el usuario no existe
    if not user:
        return None

    # Verificar que la contraseña enviada coincida con el password_hash guardado
    if not verify_password(password, user.password_hash):
        return None

    return user