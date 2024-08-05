import os
import json
import uuid
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from staffing_requirements_extractor import extract_information_from_page
from cosmos_db_service import cosmos_db_service
from datetime import datetime, timezone

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

# List all blobs in the specified folder
blob_list = container_client.list_blobs(name_starts_with=folder_path)

# Allowed file extensions
allowed_extensions = {'.docx', '.pdf'}

# Initialize a list to hold all extracted information
#all_required_roles = []
#all_role_requirements = []
#all_resume_requirements = []
blob_names = []
extracted__role_requirements_json_list = []

# Initialize sets to track duplicates
required_roles_set = set()
role_requirements_set = set()
resume_requirements_set = set()

def extract_text_for_page(page):
    text = ""
    for line in page.lines:
        text += line.content + "\n"
    return text

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

    # Analyze the file using Document Intelligence
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-layout",  # You can change this to other models like "prebuilt-invoice" or your custom model ID
        file_content
    )

    result = poller.result()

    # Process the result and extract information from each page
    previous_page_text = ""
    for i, page in enumerate(result.pages):
        current_page_text = extract_text_for_page(page)
        combined_text = previous_page_text + current_page_text

        # Use OpenAI to extract Staffing Requirements from combined text of the current and previous page
        extracted_info = extract_information_from_page(combined_text)

        if extracted_info:

            # loop through all extracted role requirements and add them to the master json list
            for role_node in extracted_info:

                role = role_node.get("required_role")

                role_added = False

                # determine if the role extracted from the LLM was not already added
                for processed_requirement_role in extracted__role_requirements_json_list:
                    if processed_requirement_role.get("required_role") == role:
                        role_added = True
                        break
                        
                # if the role wasn't already added, add it to the master list
                if (not role_added):
                    extracted__role_requirements_json_list.append(role_node)

         # Update previous_page_text. We need to do this to ensure that we don't miss any information that spans multiple pages
        previous_page_text = current_page_text 

# Generate a UUID for the document
currentDate = str(datetime.now(timezone.utc))

# Create a JSON object with aggregated information for all blobs
rfp_staffing_extract = {
    "rfpid": str(uuid.uuid4()),
    "id": str(uuid.uuid4()),
    "doc_type": "rfp_staffing_extract",
    "extract_date": currentDate,
    "status:": "rfp_extracted",
    "blob_names": blob_names,
    #"required_roles": all_required_roles,
    #"role_requirements": all_role_requirements,
    #"resume_requirements": all_resume_requirements
    "extracted_requirements": extracted_requirements_json_list
}

cosmos_db_service = cosmos_db_service()
cosmos_db_service.initialize()

created_item = cosmos_db_service.insert_rfp_staffing_extract(rfp_staffing_extract)
print(created_item)
# Convert JSON object to string
#document_json_str = json.dumps(document_json, indent=4)

# Define the path for the JSON output in the container
#json_blob_name = f"{folder_path}/{rfp_id}_rfp_staffing_extract.json"
#json_blob_client = container_client.get_blob_client(json_blob_name)

# Upload the JSON string to Azure Blob Storage
#json_blob_client.upload_blob(document_json_str, overwrite=True)

print(f"Finished processing all blobs.")
#print(f"JSON output uploaded to: {json_blob_name}\n")