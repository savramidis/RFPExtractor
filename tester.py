import datetime
import uuid
import asyncio
import os
from dotenv import load_dotenv
from cosmos_db_service import cosmos_db_service

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
endpoint = os.getenv('AZURE_COSMOS_ENDPOINT')
key = os.getenv('AZURE_COSMOS_KEY')
database_name = os.getenv('AZURE_DATABASE_NAME')
container_name = os.getenv('AZURE_CONTAINER_NAME')

# Define asynchronous test functions
async def test_insert_rf_staffing_extract(cosmos_service):
    # Example session object

    rfp_id = str(uuid.uuid4())
    currentDate = datetime.datetime.now(datetime.timezone.utc).isoformat()

    document_json = {
        "rfp_id": rfp_id,
        "doc_type": "rfp_staffing_extract",
        "extract_date": currentDate,
        "blob_names": "",
        "required_roles": "",
        "role_requirements": "",
        "resume_requirements": "",
    }

    # Insert session into Cosmos DB
    result = await cosmos_service.insert_rfp_staffing_extract_async(document_json)
    print("Insert Cosmos Result:", result)

# Main function to run tests
async def main():
    # Create an instance of the CosmosDbService
    cosmos_service = cosmos_db_service(endpoint, key, database_name, container_name)
    
    # Run tests
    await test_insert_rf_staffing_extract(cosmos_service)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())