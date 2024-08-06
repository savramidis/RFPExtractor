import os
from typing import List, Dict
from docx import Document
from cosmos_db_service import cosmos_db_service
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the OpenAI key and endpoint from environment variables
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

cosmos_db_service = cosmos_db_service()
cosmos_db_service.initialize()

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

grouped_data = cosmos_db_service.get_grouped_rfp_staffing_extract()
for rfp_id, documents in grouped_data.items():
        role_requirements = extract_staffing_requirements(documents)
        for role, requirements in role_requirements.items():
            sanitized_role = role.replace(" ", "_")
            print(f"Role: {sanitized_role}")