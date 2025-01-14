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
        """
        Inserts or updates an RFP staffing extract item in the Cosmos DB container.

        This method will insert a new item or update an existing item in the Cosmos DB container.
        If the container has not been initialized, it raises a ValueError.

        Args:
            rfp_staffing_extract (dict): The RFP staffing extract item to be inserted or updated.

        Returns:
            dict: The created or updated item.

        Raises:
            ValueError: If the CosmosDbService has not been initialized.
            exceptions.CosmosHttpResponseError: If there is an error during the upsert operation.
        """
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

    def get_all_by_rfp_id(self, rfp_id):
        if self.container is None:
            raise ValueError("The CosmosDbService has not been initialized. Call initialize() before using this method.")
        try:
           # Use a parameterized query to safely pass the rfp_id
            query = "SELECT * FROM c WHERE c.rfp_id = @rfp_id"
            parameters = [{"name": "@rfp_id", "value": rfp_id}]
        
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))

            return items
        except exceptions.CosmosHttpResponseError as e:
            logging.error(f"Failed to query items: {e.message}")
            raise

    def update_rfp_staffing_extract_status(self, item_id, rfp_id, new_value):
        if self.container is None:
            raise ValueError("The CosmosDbService has not been initialized. Call initialize() before using this method.")
        try:
            updated_item = self.container.read_item(item=item_id, partition_key=rfp_id)
            
            # Update the document (modify the fields as needed)
            updated_item['status'] = new_value

            # Replace the document in the database
            self.container.replace_item(item=updated_item, body=updated_item)

            return updated_item
        except exceptions.CosmosHttpResponseError as e:
            logging.error(f"Failed to upsert item: {e.message}")
            raise