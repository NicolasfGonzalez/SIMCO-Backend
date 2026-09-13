from models.user import User
from schemas.user import UserListResponse

# Mapper para la respuesta estándar (Crear / Actualizar)
def map_user_to_response(user):
    return {
        "id_user": user.id_user,
        "name": user.name,
        "email": user.email,
        "id_role": user.id_role,
        "role": user.role.name if user.role else "",
        "is_active": user.is_active,
        "created_at": user.created_at,
        "status": "Activo" if user.is_active else "Inactivo",
        "greenhouse_ids": [str(assignment.id_greenhouse) for assignment in user.assignments] if user.assignments else []
    }

# Mapper para la lista de usuarios (Tabla Frontend)
def map_user_to_list_response(user: User) -> UserListResponse:
    return UserListResponse(
        id_user=user.id_user,
        name=user.name,
        email=user.email,
        role=user.role.name if user.role else None,  
        status="Activo" if user.is_active else "Inactivo"  
    )

# Mapper para el detalle completo (Ver / Editar Usuario)
def map_user_to_detail_response(user):
    # Identificar el cliente del primer invernadero asignado (si tiene)
    client_id = None
    if user.assignments:
        client_id = user.assignments[0].greenhouse.id_client if user.assignments[0].greenhouse else None

    return {
        "id_user": user.id_user,
        "name": user.name,
        "email": user.email,
        "id_role": user.id_role,
        "role": user.role.name if user.role else "",
        "is_active": user.is_active,
        "status": "Activo" if user.is_active else "Inactivo", 
        "client_id": client_id,
        "greenhouse_ids": [str(assignment.id_greenhouse) for assignment in user.assignments] if user.assignments else []
    }