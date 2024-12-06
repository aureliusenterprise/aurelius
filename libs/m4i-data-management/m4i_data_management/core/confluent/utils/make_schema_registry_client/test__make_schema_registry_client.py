from .make_schema_registry_client import make_schema_registry_client

def test__make_schema_registry_client():
    client = make_schema_registry_client()
    
    assert client is not None
# END test__make_schema_registry_client
