from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.token_schemas import Token
from schemas.user import UserLogin
from services.auth_service import authenticate_user
from core.security import create_access_token
from core.database import get_db

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: UserLogin = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Autenticar las credenciales del usuario
    user = await authenticate_user(db, email=form_data.email, password=form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo en el sistema"
        )

    # Generar el Token JWT usando el UUID del usuario (id_user)
    access_token = create_access_token(subject=user.id_user)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }