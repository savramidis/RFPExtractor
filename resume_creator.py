import os
import io
import pandas as pd
import json
import requests
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

def generate_resume_content(employee_data, staffing_data):
    json_form_employee_data=str([json.dumps({
        "employee_id": "111",
        "latest_entry_date":"00:00:0",
        "latestcipolydate": "00:00:0",
        "latestfspolydate": "00:00:0",
        "certification": "AWS Certified Developer - Associate",
        "certifier_or_issuer": "Amazon Web Services",
        "issue_date": "5\\/22\\/2021",
        "expiration_date": "5\\/22\\/2024",
        "bsdl_metadata_file_path": "\\/path\\/to\\/metadata\\/file",
        "bsdl_metadata_file_name": "RAASDW_WORKER_CERTIFICATIONS_REPORT.csv",
        "bsdl_metadata_file_size": 8453085,
        "bsdl_metadata_file_modification_time": "00:16.0",
        "bsdl_date_loaded": "3\\/29\\/2023",
        "bsdl_time_loaded": "00:20.3"
    }),json.dumps({
        "employee_id": 894756,
        "latest_entry_date": "00:00.0",
        "latestcipolydate": "00:00:0",
        "latestfspolydate": "00:00:0",
        "certification": "Oracle Certified Professional, Java SE 8 Programmer",
        "certifier_or_issuer": "Oracle",
        "issue_date": "11\\/15\\/2019",
        "expiration_date": "00:00:0",
        "bsdl_metadata_file_path": "\\/path\\/to\\/metadata\\/file",
        "bsdl_metadata_file_name": "RAASDW_WORKER_CERTIFICATIONS_REPORT.csv",
        "bsdl_metadata_file_size": 8453085,
        "bsdl_metadata_file_modification_time": "00:16.0",
        "bsdl_date_loaded": "3\\/29\\/2023",
        "bsdl_time_loaded": "00:20.3"
    })])

    json_form_resume_requirements=str([json.dumps({
        "required_role": "Program Manager",
        "role_requirements": [
            {
                "requirement": "Must have current knowledge and demonstrated experience with Navy METOC operations, operational systems, applications and requirements"
            },
            {
                "requirement": "Must have at a minimum 5 years of demonstrated experience managing scientific personnel working on METOC applications"
            }
        ],
        "resume_requirements": [
            {
                "requirement": "Must have 14pt font"
            }
        ]
    }),json.dumps({
        "required_role": "Research Scientist",
        "role_requirements": [
            {
                "requirement": "NWP focus: Must act as the primary point-of-contact for the development of operational global NWP systems"
            },
            {
                "requirement": "MAP focus: Must act as the primary point-of-contact for METOC applications development including web-based applications and climatology applications"
            }
        ],
        "resume_requirements": [
            {
                "requirement": "Must be left-aligned"
            }
        ]
    })])

    json_form_matches=str([json.dumps({
        "employee_id": "111",
        "latest_entry_date":"00:00:0",
        "latestcipolydate": "00:00:0",
        "latestfspolydate": "00:00:0",
        "certification": "AWS Certified Developer - Associate",
        "certifier_or_issuer": "Amazon Web Services",
        "issue_date": "5\\/22\\/2021",
        "expiration_date": "5\\/22\\/2024",
        "bsdl_metadata_file_path": "\\/path\\/to\\/metadata\\/file",
        "bsdl_metadata_file_name": "RAASDW_WORKER_CERTIFICATIONS_REPORT.csv",
        "bsdl_metadata_file_size": 8453085,
        "bsdl_metadata_file_modification_time": "00:16.0",
        "bsdl_date_loaded": "3\\/29\\/2023",
        "bsdl_time_loaded": "00:20.3",
        "required_role": "Program Manager",
        "role_requirements": [
            {
                "requirement": "Must have current knowledge and demonstrated experience with Navy METOC operations, operational systems, applications and requirements"
            },
            {
                "requirement": "Must have at a minimum 5 years of demonstrated experience managing scientific personnel working on METOC applications"
            }
        ],
        "resume_requirements": [
            {
                "requirement": "Must have 14pt font"
            }
        ]
    }),json.dumps({
        "employee_id": 894756,
        "latest_entry_date": "00:00.0",
        "latestcipolydate": "00:00:0",
        "latestfspolydate": "00:00:0",
        "certification": "Oracle Certified Professional, Java SE 8 Programmer",
        "certifier_or_issuer": "Oracle",
        "issue_date": "11\\/15\\/2019",
        "expiration_date": "00:00:0",
        "bsdl_metadata_file_path": "\\/path\\/to\\/metadata\\/file",
        "bsdl_metadata_file_name": "RAASDW_WORKER_CERTIFICATIONS_REPORT.csv",
        "bsdl_metadata_file_size": 8453085,
        "bsdl_metadata_file_modification_time": "00:16.0",
        "bsdl_date_loaded": "3\\/29\\/2023",
        "bsdl_time_loaded": "00:20.3",
        "required_role": "Research Scientist",
        "role_requirements": [
            {
                "requirement": "NWP focus: Must act as the primary point-of-contact for the development of operational global NWP systems"
            },
            {
                "requirement": "MAP focus: Must act as the primary point-of-contact for METOC applications development including web-based applications and climatology applications"
            }
        ],
        "resume_requirements": [
            {
                "requirement": "Must be left-aligned"
            }
        ]
    })])
    

    url = f"{api_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version=2024-02-15-preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    data = {
        "messages": [
            {
                "role": "system",
                "content": f"""You are a Request for Proposal Role Matcher. Your job is to take in as input a JSON payload describing employees and a JSON payload
                    describing a roles extracted from a Request for Propoal. Each node in the employee JSON will list the certifications they hold. The employee JSON
                    will be in the following format: {json_form_employee_data}. You will check each node, which represents an employee against all roles described in
                    the roles JSON and determine which roles match the certifications held by the employee. The roles JSON will be in the following format {json_form_resume_requirements}.
                    You must inspect each nodes of the roles JSON, where the requirements are stored in the rfp_staffing_requirements node.
                    Each match must be constructed as a node and added to a JSON list and you must always and only return the matches as JSON in the following format ```{json_form_matches}```
                    where you are concatenating the two nodes together to return.
                    Ensure the JSON is properly formatted and does not contain any extra characters, malformed structures, and is properly encapsulated.
                    """
            },
            {
                "role": "user",
                "content": f"""Look through each employee in the given employee data: {employee_data}\n\n and find roles from this data: {staffing_data}\n\n which match the employees certifications."""
            }
        ],
        "max_tokens": 4000,
        "seed": 42
    }

    retry_count = 0

    json_data = ""
    while (retry_count < 3):

        # if we are retrying, send back in the json_data for the LLM to retry the format
        if (retry_count > 0):
            data = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"""The JSON you returned could not be sent into json.loads. Please take the following data and fix it: {json_data}"""
                    }
                ],
                "max_tokens": 4000,
                "seed": 42
            }

        response = requests.post(url, headers=headers, json=data)
            
        if response.status_code == 200:
            response_data = response.json()
            message_content = response_data['choices'][0]['message']['content'].strip()
            
            # Find the JSON content in the response
            try:
                message_content = str(message_content).split("```")[1]

                if message_content.startswith('json'):
                    # Remove the first occurrence of 'json' from the response text
                    message_content = message_content[4:]

                cleaned_json = message_content.replace('\n', '').replace('\\n', '').replace('\\', '').strip('"')

                json_data = json.loads(cleaned_json)

                return json_data
            except (json.JSONDecodeError, ValueError, IndexError) as e:
                print("Error: The response content is not valid JSON")
                retry_count = retry_count + 1
        else:
            response.raise_for_status()

# get employee data, assumes a detailed search
employee_data_json = get_employee_data()

# get grouped rfp staffing data
grouped_staffing_data = cosmos_db_service.get_grouped_rfp_staffing_extract()

# send employee data & rfp staffing data to OpenAI for processing
json_matches = generate_resume_content(employee_data_json, grouped_staffing_data)
print(json_matches)