from models.pile import Pile
from schemas.pile_schema import PileDetailResponse, PileListResponse

def map_pile_to_list_response(
    pile: Pile, 
    status_str: str = "Activa"
) -> PileListResponse:
    assigned_device = (
        pile.devices[0].code 
        if hasattr(pile, 'devices') and pile.devices 
        else None
    )
    
    return PileListResponse(
        id_pile=pile.id_pile,
        id_greenhouse=pile.id_greenhouse,
        code=pile.code,
        name=pile.name or f"Pila {pile.code}",
        process_start_date=pile.process_start_date,
        created_at=pile.created_at,
        assigned_device_code=assigned_device,
        status=status_str
    )

def map_pile_to_detail_response(
    pile: Pile, 
    mongo_doc: dict = None, 
    latest_telemetry: dict = None
) -> PileDetailResponse:
    assigned_device = (
        pile.devices[0].code 
        if hasattr(pile, 'devices') and pile.devices 
        else None
    )
    
    # Manejo seguro de datos provenientes de MongoDB
    doc = mongo_doc or {}
    loc = doc.get("location")
    est_date = doc.get("estimated_end_date")
    st = doc.get("status", "Activa")
    mat = doc.get("base_material")
    nts = doc.get("notes")

    # Extraer únicamente los datos numéricos de lecturas
    readings = None
    if latest_telemetry and isinstance(latest_telemetry, dict):
        readings = latest_telemetry.get("readings")

    return PileDetailResponse(
        id_pile=pile.id_pile,
        id_greenhouse=pile.id_greenhouse,
        code=pile.code,
        name=pile.name or f"Pila {pile.code}",
        process_start_date=pile.process_start_date,
        created_at=pile.created_at,
        assigned_device_code=assigned_device,
        location=loc,
        estimated_end_date=est_date,
        status=st,
        base_material=mat,
        notes=nts,
        latest_readings=readings
    )