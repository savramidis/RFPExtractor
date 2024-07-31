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
    
    systemPrompt = "You are an AI Assistant. Your job is to take in as input data from a Request for Proposal and Extract the Staffing Requirements which can include Required Roles, Role Requirements, and Resume Requirements from the following text. Provide the output in JSON format with keys required_roles, role_requirements, and resume_requirements. Only return valid JSON."
    userPrompt = "Extract the Staffing Requirements from the following text"

    # Payload for the request
    url = f"{api_endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version=2023-05-15"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    data = {
        "messages": [
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": f"{userPrompt}:\n\n{page_text}"}
        ],
        "max_tokens": 1024,
        "temperature": 0.5
    }

    response = requests.post(url, headers=headers, json=data)
       
    if response.status_code == 200:
        response_data = response.json()
        message_content = response_data['choices'][0]['message']['content'].strip()
        
        # Find the JSON content in the response
        try:
             # Find the JSON content in the response
            json_start = message_content.find('{')
            json_end = message_content.rfind('}') + 1
            json_content = message_content[json_start:json_end]

            # Parse the JSON content
            extracted_info = json.loads(json_content)
            print(extracted_info)
        except (json.JSONDecodeError, ValueError, IndexError) as e:
            print("Error: The response content is not valid JSON")
            return None

        return extracted_info
    else:
        response.raise_for_status()