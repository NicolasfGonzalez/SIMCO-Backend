from schemas.client_schema import ClientBasicResponse, ClientResponse
from models.client import Client


def map_client_to_basic_response(client):
    return ClientBasicResponse(
        id=client.id_client,
        name=client.name
    )

def map_clients_to_basic_response(clients):
    return [map_client_to_basic_response(c) for c in clients]

def map_client_to_response(client: Client) -> ClientResponse:
    return ClientResponse(
        id_client=client.id_client,
        name=client.name,
        email=client.email,
        phone=client.phone,
        created_at=client.created_at
    )

def map_client_to_basic_response(client: Client) -> ClientBasicResponse:
    return ClientBasicResponse(
        id=client.id_client,
        name=client.name
    )