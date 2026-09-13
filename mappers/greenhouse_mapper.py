from models.greenhouse import Greenhouse
from schemas.greenhouse_schema import (
    GreenhouseCrudListResponse, 
    GreenhouseDetailResponse
)

# Mapper para la lista de invernaderos (DataGrid del Frontend)
def map_greenhouse_to_list_response(gh: Greenhouse) -> GreenhouseCrudListResponse:
    # Extraemos solo los nombres de los usuarios responsables
    nombres_responsables = []
    if gh.assignments:
        nombres_responsables = [
            asignacion.user.name for asignacion in gh.assignments if asignacion.user
        ]

    return GreenhouseCrudListResponse(
        id_greenhouse=gh.id_greenhouse,
        name=gh.name,
        location=gh.location or "Sin ubicación",
        is_active=gh.is_active,
        status="Activo" if gh.is_active else "Inactivo",
        responsables=nombres_responsables
    )

# Mapper para el detalle (Modal de edición / Botón Detalles)
def map_greenhouse_to_detail_response(gh: Greenhouse) -> GreenhouseDetailResponse:
    nombres_responsables = []
    if gh.assignments:
        nombres_responsables = [
            asignacion.user.name for asignacion in gh.assignments if asignacion.user
        ]

    return GreenhouseDetailResponse(
        id_greenhouse=gh.id_greenhouse,
        id_client=gh.id_client,
        name=gh.name,
        location=gh.location or "",
        latitude=gh.latitude or 0.0,
        longitude=gh.longitude or 0.0,
        is_active=gh.is_active,
        status="Activo" if gh.is_active else "Inactivo",
        created_at=gh.created_at,
        responsables=nombres_responsables
    )