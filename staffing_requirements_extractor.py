import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the OpenAI key and endpoint from environment variables
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

def extract_information_from_page(page_text):
    url = f"{api_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version=2024-02-15-preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    systemPrompt = "You are an AI Assistant. Your job is to take in as input data from a Request for Proposal and Extract the Staffing Requirements which can include Required Roles, Role Requirements, and Resume Requirements from the following text. Provide the output in JSON format with keys 'required_roles', 'role_requirements', and 'resume_requirements'."
    userPrompt = "Extract the Staffing Requirements from the following text"

    # Payload for the request
    payload = {
    "messages": [
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "prompt": systemPrompt,
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "content": f"{userPrompt}: {page_text}"
            }
        ]
        }
    ],
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 800
    }
    
    jsonPayload = json.dumps(payload)
    response = requests.post(url, headers=headers, data=jsonPayload)
    
    if response.status_code == 200:
        response_data = response.json()
        message_content = response_data['choices'][0]['message']['content'].strip()
        
        try:
            extracted_info = json.loads(message_content)
        except json.JSONDecodeError:
            raise ValueError("The response content is not valid JSON")

        return extracted_info
    else:
        response.raise_for_status()