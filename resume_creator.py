import os
import io
import pandas as pd
from azure.storage.blob import BlobServiceClient, ContainerClient
from typing import List, Dict
from docx import Document
from cosmos_db_service import cosmos_db_service
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# Load environment variables from the .env file
load_dotenv()

# Get the OpenAI key and endpoint from environment variables
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Get environment variables
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
folder_path = "employee_data"

cosmos_db_service = cosmos_db_service()
cosmos_db_service.initialize()

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Get a client to interact with the container
container_client = blob_service_client.get_container_client(container_name)

def get_employee_data():
    # Initialize the BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # List all blobs in the specified folder
    blob_list = container_client.list_blobs(name_starts_with=folder_path)
    
    # Allowed file extensions
    allowed_extensions = {'.csv'}
    
    # Dictionary to hold the JSON data
    json_data = {}

    for blob in blob_list:
        # Check file extension
        _, file_extension = os.path.splitext(blob.name)
        if file_extension.lower() not in allowed_extensions:
            print(f"Skipping blob: {blob.name} (unsupported file type)")
            continue

        print(f"Processing blob: {blob.name}")

        # Create a BlobClient for the specific blob
        blob_client = container_client.get_blob_client(blob)

        # Download the blob's content
        download_stream = blob_client.download_blob()
        file_content = download_stream.readall()

        # Convert the file content to a pandas DataFrame
        file_name = os.path.basename(blob.name)
        df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))

        # Convert the DataFrame to JSON and store it in the dictionary
        json_data[file_name] = df.to_json(orient='records')

    return json_data

def extract_staffing_requirements(documents: List[Dict]) -> Dict[str, List[Dict]]:
    role_requirements = {}
    for doc in documents:
        requirements = doc.get('rfp_staffing_requirements', [])
        for req in requirements:
            role = req.get('required_role', 'Unknown Role')
            if role not in role_requirements:
                role_requirements[role] = []
            role_requirements[role].extend(req.get('role_requirements', []))

    return role_requirements

# get employee data, assumes a detailed search
employee_data_json = get_employee_data()

# get grouped rfp staffing data
grouped_staffing_data = cosmos_db_service.get_grouped_rfp_staffing_extract()

# send employee data & rfp staffing data to OpenAI for processing