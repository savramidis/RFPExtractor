import os
import json
import uuid
from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from staffing_requirements_extractor import extract_information_from_page  # Import the function

# Load environment variables from the .env file
load_dotenv()

# Get environment variables
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
form_recognizer_endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
form_recognizer_key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
folder_path = os.getenv("AZURE_STORAGE_FOLDER")

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Get a client to interact with the container
container_client = blob_service_client.get_container_client(container_name)

# Initialize DocumentAnalysisClient
document_analysis_client = DocumentAnalysisClient(
    endpoint=form_recognizer_endpoint,
    credential=AzureKeyCredential(form_recognizer_key)
)

# List all blobs in the container
blob_list = container_client.list_blobs(name_starts_with=folder_path)

for blob in blob_list:
    print(f"Processing blob: {blob.name}")
    
    # Create a BlobClient for the specific blob
    blob_client = container_client.get_blob_client(blob)

    # Download the blob's content
    download_stream = blob_client.download_blob()
    file_content = download_stream.readall()

    # Analyze the file using Document Intelligence
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-layout",  # You can change this to other models like "prebuilt-invoice" or your custom model ID
        file_content
    )
    result = poller.result()

    # Generate a UUID and create the JSON object
    rfp_id = str(uuid.uuid4())

    # Initialize a list to hold page data
    pages_data = []

    # Process the result and build JSON structure
    for page in result.pages:
        page_data = {
            "page_number": page.page_number,
            "lines": []
        }
        for line in page.lines:
            page_data["lines"].append(line.content)
        pages_data.append(page_data) 

    document_json = {
        "rfp_id": rfp_id,
        "blob_name": blob.name,
        "pages": pages_data
    }

    # Convert JSON object to string
    document_json_str = json.dumps(document_json, indent=4)

 # Define the path for the JSON output in the same folder
    json_blob_name = os.path.splitext(blob.name)[0] + "extract.json"
    json_blob_client = container_client.get_blob_client(json_blob_name)

    # Upload the JSON string to Azure Blob Storage
    json_blob_client.upload_blob(document_json_str, overwrite=True)