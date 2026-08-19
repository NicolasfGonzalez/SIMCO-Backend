from schemas.client_schema import ClientBasicResponse

def map_client_to_basic_response(client):
    return ClientBasicResponse(
        id=client.id_client,
        name=client.name
    )

def map_clients_to_basic_response(clients):
    return [map_client_to_basic_response(c) for c in clients]