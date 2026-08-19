from models.user import User
from schemas.user import UserResponse
from schemas.user import UserListResponse

# Mapper Funcion para convertir un objeto User a UserResponse
def map_user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id_user=user.id_user,
        name=user.name,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        role=user.role.name if user.role else None,
        client=user.client.name if user.client else None
    )


# Mapper Funcion para lista de usuarios
def map_user_to_list_response(user: User) -> UserListResponse:
    return UserListResponse(
        id_user=user.id_user,
        name=user.name,
        email=user.email,
        role=user.role.name,  
        status="Activo" if user.is_active else "Inactivo"  
    )

# Mapper 
def map_user_to_detail_response(user):

    return {

        "id_user":user.id_user,

        "name":user.name,

        "email":user.email,


        "id_role":user.id_role,

        "role":
            user.role.name
            if user.role else None,


        "id_client":user.id_client,

        "client":
            user.client.name
            if user.client else None,


        "status":
            "Activo"
            if user.is_active
            else "Inactivo"
    }