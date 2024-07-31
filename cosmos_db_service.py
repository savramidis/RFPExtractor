from azure.cosmos import exceptions
from azure.cosmos.aio import CosmosClient

class cosmos_db_service:
    def __init__(self, endpoint, key, database_name, container_name):
        if not all([endpoint, key, database_name, container_name]):
            raise ValueError("All parameters must be provided and non-empty.")
        
        client = CosmosClient(endpoint, credential=key)
        try:
            database = client.get_database_client(database_name)
            self.container = database.get_container_client(container_name)
        except exceptions.CosmosResourceNotFoundError:
            raise ValueError("Database or Container does not exist.")

    async def insert_rfp_staffing_extract_async(self, session):
        created_item = await self.container.upsert_item(body=session)
        return created_item