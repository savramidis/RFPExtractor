import time
import os
import uuid
from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from staffing_requirements_extractor import extract_information_from_page
from cosmos_db_service import cosmos_db_service
from datetime import datetime, timezone
from requests.exceptions import HTTPError

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

cosmos_db_service = cosmos_db_service()
cosmos_db_service.initialize()

# List all blobs in the specified folder
blob_list = container_client.list_blobs(name_starts_with=folder_path)

# Allowed file extensions
allowed_extensions = {'.docx', '.pdf'}

# Initialize a list to hold all extracted information
blob_names = []
extracted_role_requirements_json_list = []

# Initialize sets to track duplicates
required_roles_set = set()
role_requirements_set = set()
resume_requirements_set = set()
rfp_id = str(uuid.uuid4())

def analyze_document_with_retry(document_analysis_client, file_content, retries=5):
    attempt = 0
    while attempt < retries:
        try:
            poller = document_analysis_client.begin_analyze_document(
                "prebuilt-layout",
                file_content
            )
            result = poller.result()
            return result
        except HTTPError as e:
            if e.response.status_code == 429:
                attempt += 1
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise

for blob in blob_list:
    # Check file extension
    _, file_extension = os.path.splitext(blob.name)
    if file_extension.lower() not in allowed_extensions:
        print(f"Skipping blob: {blob.name} (unsupported file type)")
        continue

    print(f"Processing blob: {blob.name}")
    blob_names.append(str(blob.name))

    # Create a BlobClient for the specific blob
    blob_client = container_client.get_blob_client(blob)

    # Download the blob's content
    download_stream = blob_client.download_blob()
    file_content = download_stream.readall()

    # Analyze the file using Document Intelligence with retry
    result = analyze_document_with_retry(document_analysis_client, file_content)

    extracted_info = extract_information_from_page(result.content)

    if extracted_info:
        currentDate = str(datetime.now(timezone.utc))

        # Wrap the list into a single document
        single_document = {
            "id": str(uuid.uuid4()),
            "rfp_id": rfp_id,
            "doc_type": "rfp_staffing_extract",
            "extract_date": currentDate,
            "status": "rfp_extracted",
            "blob_name": str(blob.name),
            "rfp_staffing_requirements": extracted_info
        }

        created_item = cosmos_db_service.insert_rfp_staffing_extract(single_document)
        print(created_item)

print(f"Finished processing all blobs.")