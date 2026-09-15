from models.greenhouse import Greenhouse
from schemas.greenhouse_schema import (
    GreenhouseCrudListResponse,
    GreenhouseDetailResponse
)

def map_greenhouse_to_list_response(gh: Greenhouse) -> GreenhouseCrudListResponse:
    responsables = []
    if gh.assignments:
        responsables = [asig.user.name for asig in gh.assignments if asig.user]

    return GreenhouseCrudListResponse(
        id_greenhouse=gh.id_greenhouse,
        name=gh.name,
        address=gh.address or "Sin dirección",
        is_active=gh.is_active,
        status="Activo" if gh.is_active else "Inactivo",
        responsables=responsables
    )

def map_greenhouse_to_detail_response(gh: Greenhouse) -> GreenhouseDetailResponse:
    nombres_responsables = []
    ids_responsables = []
    
    if gh.assignments:
        nombres_responsables = [
            asignacion.user.name for asignacion in gh.assignments if asignacion.user
        ]
        ids_responsables = [
            asignacion.user.id_user for asignacion in gh.assignments if asignacion.user
        ]

    return GreenhouseDetailResponse(
        id_greenhouse=gh.id_greenhouse,
        id_client=gh.id_client,
        name=gh.name,
        address=gh.address or "",
        latitude=gh.latitude or 0.0,
        longitude=gh.longitude or 0.0,
        is_active=gh.is_active,
        status="Activo" if gh.is_active else "Inactivo",
        created_at=gh.created_at,
        responsables=nombres_responsables,
        responsables_ids=ids_responsables
    )