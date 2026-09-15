from models.user import User
from schemas.user import UserListResponse


# RESPUESTA GENERAL
def map_user_to_response(user: User):

    return {
        "id_user": user.id_user,
        "name": user.name,
        "email": user.email,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "role": user.role.name if user.role else "",
        "client": None,
    }


# RESPUESTA PARA LISTADO
def map_user_to_list_response(
    user: User
) -> UserListResponse:

    return UserListResponse(
        id_user=user.id_user,
        name=user.name,
        email=user.email,
        role=user.role.name if user.role else None,
        status=(
            "Activo"
            if user.is_active
            else "Inactivo"
        )
    )


# RESPUESTA DE DETALLE
def map_user_to_detail_response(
    user: User,
    client_id=None
):

    return {
        "id_user": user.id_user,
        "name": user.name,
        "email": user.email,
        "id_role": user.id_role,
        "role": (
            user.role.name
            if user.role
            else ""
        ),
        "is_active": user.is_active,
        "status": (
            "Activo"
            if user.is_active
            else "Inactivo"
        ),
        "client_id": client_id,
        "greenhouse_ids": [
            str(assignment.id_greenhouse)
            for assignment in user.assignments
        ] if user.assignments else []
    }