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
    json_form_employee_data=str([json.dumps({
        "certs.csv": [
            {
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
            },
            {
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
            }
        ],
        "education.csv": [
           {
                "employee_id": 894756,
                "highest_degree": "Bachelors",
                "latest_entry_date": "00:00.0",
                "school_attended": "University of California, Berkeley",
                "school_location": "United States of America",
                "degree": "Bachelor Degree",
                "field_of_study": "Computer Science",
                "bsdl_metadata_file_path": "\\/path\\/to\\/azure\\/blob\\/storage\\/RAASDW_WORKER_DEGREES_REPORT.csv",
                "bsdl_metadata_file_name": "RAASDW_WORKER_DEGREES_REPORT.csv",
                "bsdl_metadata_file_size": 7508269,
                "bsdl_metadata_file_modification_time": "00:16.0",
                "bsdl_date_loaded": "3\\/30\\/2023",
                "bsdl_time_loaded": "00:20.3"
            },
            {
                "employee_id": 475839,
                "highest_degree": "Masters",
                "latest_entry_date": "00:00.0",
                "school_attended": "University of Maryland",
                "school_location": "United States of America",
                "degree":"Bachelor\'s Degree",
                "field_of_study": "Information Technology",
                "bsdl_metadata_file_path": "\\/path\\/to\\/azure\\/blob\\/storage\\/RAASDW_WORKER_DEGREES_REPORT.csv",
                "bsdl_metadata_file_name": "RAASDW_WORKER_DEGREES_REPORT.csv",
                "bsdl_metadata_file_size": 7508269,
                "bsdl_metadata_file_modification_time": "00:16.0",
                "bsdl_date_loaded": "3\\/31\\/2023",
                "bsdl_time_loaded": "00:20.3"
            }
        ],
        "skills.csv": [
            {
                "emplid": 894756,
                "current_effective_date": "00:00.0",
                "skill": "Python",
                "skill_type": "Internal",
                "bsdl_metadata_file_path": "https:\\/\\/azure.blob.storage\\/INT0014_WORKER_SKILLS.dat",
                "bsdl_metadata_file_name": "INT0014_WORKER_SKILLS.dat",
                "bsdl_metadata_file_size": 55513314,
                "bsdl_metadata_file_modification_time": "30:19.0",
                "badl_date_loaded": "4\\/1\\/2023",
                "bsdl_time_loaded": "30:28.0"
            },
            {
                "emplid": 894756,
                "current_effective_date": "00:00.0",
                "skill": "Java",
                "skill_type": "Internal",
                "bsdl_metadata_file_path": "https:\\/\\/azure.blob.storage\\/INT0014_WORKER_SKILLS.dat",
                "bsdl_metadata_file_name": "INT0014_WORKER_SKILLS.dat",
                "bsdl_metadata_file_size": 55513314,
                "bsdl_metadata_file_modification_time": "30:19.0",
                "badl_date_loaded": "4\\/1\\/2023",
                "bsdl_time_loaded": "30:28.0"
            }
        ],
        "work_history.csv": [
            {
                "employeeID": 894756,
                "workdayID": "5e12f540-8db1-44e8-99f3-d5ff4c5b4d99",
                "worker_id": "5e12f540-8db1-44e8-99f3-d5ff4c5b4d99",
                "worker_descriptor": "John Doe (894756)",
                "startDate": "2021-03-15",
                "endDate": "null",
                "responsibilitiesAndAchievements": "Developed and maintained scalable software solutions. Collaborated with cross-functional teams to define, design, and ship new features. Ensured the performance, quality, and responsiveness of applications. Identified and corrected bottlenecks and fixed bugs.",
                "skillWorkdayID": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
                "company": "Booz Allen Hamilton",
                "enteredOn": "2023-04-01",
                "jobTitle": "Mid-Level Software Engineer",
                "skillReferenceID": "2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e",
                "source_id": "3c4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
                "source_descriptor": "Self",
                "externalJob_id": "4d5e6f7a-8b9c-0d1e-2f3a4b5c6d7e",
                "externalJob_descriptor": "Mid-Level Software Engineer",
                "bsdl_date_loaded": "2023-04-01",
                "bsdl_time_loaded": "2023-04-01T08:10:00Z",
                "bsdl_load_id": "5e6f7a8b-9c0d-1e2f-3a4b5c6d7e8f"
            },
            {
                "employeeID": 894756,
                "workdayID": "5e12f540-8db1-44e8-99f3-d5ff4c5b4d99",
                "worker_id": "5e12f540-8db1-44e8-99f3-d5ff4c5b4d99",
                "worker_descriptor": "John Doe (894756)",
                "startDate": "2019-08-01",
                "endDate": "2021-03-14",
                "responsibilitiesAndAchievements": "Participated in the full software development lifecycle, from concept to deployment in a collaborative environment. Implemented backend services for web applications. Wrote clean, maintainable code and performed peer code-reviews.",
                "skillWorkdayID": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
                "company": "Acme Corp",
                "enteredOn": "2023-04-01",
                "jobTitle": "Software Engineer",
                "skillReferenceID": "2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e",
                "source_id": "3c4d5e6f-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
                "source_descriptor": "Recruiting",
                "externalJob_id": "4d5e6f7a-8b9c-0d1e-2f3a4b5c6d7e",
                "externalJob_descriptor": "Software Engineer",
                "bsdl_date_loaded": "2023-04-01",
                "bsdl_time_loaded": "2023-04-01T08:15:00Z",
                "bsdl_load_id": "5e6f7a8b-9c0d-1e2f-3a4b5c6d7e8f"
            }
        ]
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
        "highest_degree": "Bachelors",
        "school_attended": "University of California, Berkeley",
        "field_of_study": "Computer Science",
        "skill": "Python",
        "worker_description": "John Doe (894756)",
        "responsibilitiesAndAchievements": "Developed and maintained scalable software solutions. Collaborated with cross-functional teams to define, design, and ship new features. Ensured the performance, quality, and responsiveness of applications. Identified and corrected bottlenecks and fixed bugs.",
        "company": "Booz Allen Hamilton",
        "jobTitle": "Mid-Level Software Engineer",
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
        "highest_degree": "Bachelors",
        "school_attended": "University of Michigan",
        "field_of_study": "Computer Science",
        "skill": ".NET",
        "worker_description": "Jane Doe (894756)",
        "responsibilitiesAndAchievements": "Developed and maintained scalable software solutions. Collaborated with cross-functional teams to define, design, and ship new features. Ensured the performance, quality, and responsiveness of applications. Identified and corrected bottlenecks and fixed bugs.",
        "company": "Northrop Grumman",
        "jobTitle": "Mid-Level Software Engineer",
        "bsdl_metadata_file_path": "\\/path\\/to\\/metadata\\/file",
        "bsdl_metadata_file_name": "RAASDW_WORKER_CERTIFICATIONS_REPORT.csv",
        "bsdl_metadata_file_size": 8453085,
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

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "system",
                "content": f"""You are a Request for Proposal Role Matcher. Your job is to take in as input a JSON payload describing employees and a JSON payload
                    describing a roles extracted from a Request for Propoal. Each node in the employee JSON will list the certifications they hold, their education,
                    their skills, and their work history. The employee JSON will be in the following format: {json_form_employee_data}. You will check each node, 
                    which represents an employee against all roles described in the roles JSON and determine which roles match the employee's details. The roles JSON
                    will be in the following format {json_form_resume_requirements}. You must inspect each nodes of the roles JSON, where the requirements are stored
                    in the rfp_staffing_requirements node. Each match must be constructed as a node and added to a JSON list and you must always and only return the
                    matches as JSON in the following format ```{json_form_matches}``` where you are concatenating the two nodes together to return.
                    Ensure the JSON is properly formatted and does not contain any extra characters, malformed structures, and is properly encapsulated.
                    """
            },
            {
                "role": "user",
                "content": f"""Look through each employee in the given employee data: {employee_data}\n\n and find roles from this data: {staffing_data}\n\n which match the employees certifications."""
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

    # resume template to fill in
    blob_name = "test.docx"

    # Create the BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create a blob client using the blob name and container name
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Download the blob to an in-memory byte stream
    blob_data = blob_client.download_blob().readall()
    byte_stream = BytesIO(blob_data)

    # Load the in-memory byte stream into python-docx
    document = Document(byte_stream)

    for paragraph in document.paragraphs:
        print(paragraph.text)

# get employee data, assumes a detailed search
employee_data_json = get_employee_data()

# get grouped rfp staffing data
grouped_staffing_data = cosmos_db_service.get_grouped_rfp_staffing_extract()

# send employee data & rfp staffing data to OpenAI for processing
json_matches = generate_resume_content(employee_data_json, grouped_staffing_data)

if (json_matches):
    create_resume(json_matches)