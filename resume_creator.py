import os
import io
import pandas as pd
import json
from openai import AzureOpenAI
from azure.storage.blob import BlobServiceClient
from typing import List, Dict
from docx import Document
from cosmos_db_service import cosmos_db_service
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from io import BytesIO

# Load environment variables from the .env file
load_dotenv()

# Get the OpenAI key and endpoint from environment variables
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
resume_template = os.getenv("RESUME_TEMPLATE")

client = AzureOpenAI(
    api_key=api_key,
    # per comment in staffing requirements extractor, when the 2024-08-06 API is available, we'll switch to that to use structured output
    api_version="2024-02-15-preview",
    azure_endpoint=api_endpoint
)

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
    
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "system",
                'content': """You are a helpful AI assistant that specializes in generating resumes for employees from a database of employee records.
                You will be provided with a JSON object that contains the employee's certifications, education, skills, and work history.
                The JSON object will have the following keys: certifications, education, skills, and employment_history.
                Each value in the JSON object will be a tab-separated string that contains the data for the respective category.
                Here is an example:
                {
                    "certifications": "Project Management Professional, 2011 - Present",
                    "education": "MPA, School of Public and Environmental Affairs, Indiana University, 2010",
                    "skills": "Data Mining",
                    "employment_history": "Booz Allen Hamilton, Senior Consultant, 2010 - Present",
                    "security_clearances": "Secret"
                }
                You will also be provided a JSON that has information about a position's requirements for education, certifications, experience, and security clearances.
                Here is an example:
                {
                    "required_role": "Program Manager (Key Personnel)",
                    "education": {
                        "Degree": "M.S.",
                        "Field": [
                            "Meteorology",
                            "Oceanography",
                            "Physical Science",
                            "Mathematics",
                            "Engineering"
                        ]
                    },
                    "certifications": [],
                    "experience": [
                        {"requirement": "Must have current knowledge and demonstrated experience with Navy METOC operations, operational systems, applications and requirements"},
                        {"requirement": "Must have at a minimum 5 years of demonstrated experience managing scientific, engineering, computing, and technical personnel working on Numerical Weather Prediction (NWP) and METOC applications development projects"}
                    ],
                    "security_clearance": []
                }
                Your task is to generate a JSON object that contains a resume for each employee that satisfies the requirements for the given positions. This should be a list of JSON objects where each item in the list represents a candidate resume. YOu s
                The JSON should have the following format:
                {
                    "name": The name of the employee. Do not include the employee id in the name.,
                    "employee_id": The employee's id.,
                    "professional_summary": This should be a string that summarizes the employee's professional experience. This summary should emphasize the employee's qualifications for the position.,
                    "key_competencies": This should be a list of strings from the employee's skills. Include only the skills that are relevant to the position.,
                    "education": This should be a list of strings in the format "Degree earned, Field of study, School Attended, Date of graduation",
                    "certifications": This should be a list of strings from the employee's certifications,
                    "relevant_experience": This should be a list of strings from the employment_history's responsibilitiesAndAchievements that match the experience requirements. Do not include employment history that is not relevant to the position,
                    "employment_history": This should be a list of strings in the format "Company, Title, Start Date - End Date",
                    "years_of_experience": The total number of years the employee has worked in the field. This should be calculated from the employment_history's startDate and endDate,
                    "years_of_relevant_experience": The total number of years the employee has worked in a relevant position. This should be calculated from the employment_history's startDate and endDate,
                    "security_clearances": This should be a list of strings from the security_clearances,
                }
                Do not include information you do not know. Do not include information about the employee that is not provided in the employee data.
                Your response should be in JSON format and include only the JSON."""
            },
            {
                "role": "user",
                "content": f"""Generate a list of candidate resumes using the following employee data employee data: {employee_data}\n\n and find roles from this data: {staffing_data}\n\n which match the employees certifications."""
            }
        ],
        max_tokens=4000,
        seed=42
    )
    
    retry_count = 0
    json_data = {}
    cleaned_json = {}

    while (retry_count < 3):

        # if we are retrying, send back in the json_data for the LLM to retry the format
        if (retry_count > 0):
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {
                        "role": "user",
                        "content": f"""The JSON you returned could not be sent into json.loads. Please take the following data and fix it: {cleaned_json}"""
                    }
                ],
                max_tokens=4000,
                seed=42
            )
    
        message_content = response.choices[0].message.content.strip()
            
        # Find the JSON content in the response
        try:
            message_content = str(message_content).split("```")[1]

            if message_content.startswith('json'):
                # Remove the first occurrence of 'json' from the response text
                message_content = message_content[4:]

            cleaned_json = message_content.replace('\n', '').replace('\\n', '').replace('\\', '').strip('"')

            json_data = json.loads(cleaned_json)

            #cleaned_json = json.dumps(json_data, indent=4)
            #print(cleaned_json)

            return json_data
        except (json.JSONDecodeError, ValueError, IndexError) as e:
            print("Error: The response content is not valid JSON")
            retry_count = retry_count + 1

    print("Retry count exceeded!")

def create_resume(json_matches):
    print(json.dumps(json_matches, indent=4))

    # Create the BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create a blob client using the blob name and container name
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=resume_template)

    # Download the blob to an in-memory byte stream
    blob_data = blob_client.download_blob().readall()
    byte_stream = BytesIO(blob_data)

    # Load the in-memory byte stream into python-docx
    document = Document(byte_stream)

    name = json_matches['name']
    education = json_matches["education"]
    key_competencies = json_matches["key_competencies"]
    certifications = json_matches["certifications"]

    professional_summary = json_matches["professional_summary"]
        
    for paragraph in document.paragraphs:
        if 'Name, Credential (if any)' in paragraph.text:
            paragraph.text = paragraph.text.replace('Name, Credential (if any)', name)
            paragraph.text += "\n" + professional_summary
            
        for table in document.tables:
            for row in table.rows:
                # Check the leftmost cell (first cell) for the search text
                left_cell = row.cells[0]
                for paragraph in left_cell.paragraphs:
                    if 'Key Competencies' in paragraph.text:
                        # If found, set the text in the rightmost cell
                        right_cell = row.cells[-1]
                        for right_paragraph in right_cell.paragraphs:
                            key_competencies_str = "\n".join(key_competencies)
                            right_paragraph.text = key_competencies_str
                            break

                    if 'Education' in paragraph.text:
                        # If found, set the text in the rightmost cell
                        right_cell = row.cells[-1]
                        for right_paragraph in right_cell.paragraphs:
                            education_str = "\n".join(education)
                            right_paragraph.text = education_str
                            break

                    if 'Training & Certifications' in paragraph.text:
                        # If found, set the text in the rightmost cell
                        right_cell = row.cells[-1]
                        for right_paragraph in right_cell.paragraphs:
                            certifications_str = "\n".join(certifications)
                            right_paragraph.text = certifications_str
                            break

    # Save the updated document to a new in-memory byte stream
    byte_stream = io.BytesIO()
    document.save(byte_stream)
    byte_stream.seek(0)

    blob_client = container_client.get_blob_client(name + "_Resume.docx")
    blob_client.upload_blob(byte_stream, overwrite=True)

# get employee data, assumes a detailed search
employee_data_json = get_employee_data()

# get grouped rfp staffing data
grouped_staffing_data = cosmos_db_service.get_grouped_rfp_staffing_extract()

# send employee data & rfp staffing data to OpenAI for processing
json_matches = generate_resume_content(employee_data_json, grouped_staffing_data)

if (json_matches):
    # need a for each here
    for match in json_matches:
        create_resume(match)