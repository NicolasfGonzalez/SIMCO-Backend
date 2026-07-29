from models.role import Role
from schemas.role_schema import RoleOut


def role_to_schema(role: Role) -> RoleOut:
    return RoleOut(
        id_role=role.id_role,
        name=role.name
    )


def roles_to_schema(roles: list[Role]) -> list[RoleOut]:
    return [
        role_to_schema(role)
        for role in roles
    ]