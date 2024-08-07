import os
import logging
from azure.cosmos import exceptions, CosmosClient

logging.basicConfig(level=logging.INFO)

class cosmos_db_service:
    def __init__(self):
        self.endpoint = os.getenv('AZURE_COSMOS_ENDPOINT')
        self.key = os.getenv('AZURE_COSMOS_KEY')
        self.database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME')
        self.container_name = os.getenv('AZURE_COSMOS_CONTAINER_NAME')
        
        if not all([self.endpoint, self.key, self.database_name, self.container_name]):
            raise ValueError("All environment variables must be provided and non-empty.")
        
        self.client = CosmosClient(self.endpoint, credential=self.key)
        self.container = None  # Initialize the container attribute

    def initialize(self):
        try:
            database = self.client.get_database_client(self.database_name)
            self.container = database.get_container_client(self.container_name)
        except exceptions.CosmosResourceNotFoundError:
            raise ValueError("Database or Container does not exist.")
        except Exception as e:
            logging.error(f"Failed to initialize Cosmos DB service: {e}")
            raise

    def insert_rfp_staffing_extract(self, rfp_staffing_extract):
        if self.container is None:
            raise ValueError("The CosmosDbService has not been initialized. Call initialize() before using this method.")
        try:
            created_item = self.container.upsert_item(body=rfp_staffing_extract)
            return created_item
        except exceptions.CosmosHttpResponseError as e:
            logging.error(f"Failed to upsert item: {e.message}")
            raise

    def get_grouped_rfp_staffing_extract(self):
        if self.container is None:
            raise ValueError("The CosmosDbService has not been initialized. Call initialize() before using this method.")
        try:
            items = list(self.container.query_items(
                query="SELECT * FROM c WHERE c.status = 'rfp_extracted'",
                enable_cross_partition_query=True))
            
            grouped_data = {}
            for item in items:
                rfp_id = item['rfp_id']
                if rfp_id not in grouped_data:
                    grouped_data[rfp_id] = []
                grouped_data[rfp_id].append(item)
    
            return grouped_data
        except exceptions.CosmosHttpResponseError as e:
            logging.error(f"Failed to query items: {e.message}")
            raise

    def update_rfp_staffing_extract(self, item_id, rfp_id, field, new_value):
        if self.container is None:
            raise ValueError("The CosmosDbService has not been initialized. Call initialize() before using this method.")
        try:
            updated_item = self.container.read_item(item=item_id, partition_key=rfp_id)
            
            # Update the document (modify the fields as needed)
            updated_item[field] = new_value

            # Replace the document in the database
            self.container.replace_item(item=updated_item, body=updated_item)

            return updated_item
        except exceptions.CosmosHttpResponseError as e:
            logging.error(f"Failed to upsert item: {e.message}")
            raise