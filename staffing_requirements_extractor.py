import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the OpenAI key and endpoint from environment variables
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

def extract_information_from_page(page_text):

    json_form=str([json.dumps({
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

    client = AzureOpenAI(
        api_key=api_key,
        # per comment below, when the 2024-08-06 API is available, we'll switch to that to use structured output
        api_version="2024-02-15-preview",
        azure_endpoint=api_endpoint
    )

    # this prompt is used for sending in a single RFP document without the need to chunk
    response = client.chat.completions.create(
         model=deployment_name,
         #response_format={"type":"json_object"},
         messages=[
             {
                "role": "system",
                "content": f"""You are a Request for Proposal Requirements Extractor expert. Your job is to take in as input a a Request for Proposal
                    and Extract the Staffing Requirements. You must only extract data that exists in the RFP, do not make anything up.
                    Always check the parent child relationship of the roles so that the full role title is specified. You must always combine these two. If Example:
                    1. Engineer
                    1.1 Senior
                    This example would result in a role titled: Senior Engineer. You must never return just Engineer.  
                    Always check if the role is labeled as Key Personnel and add that to the title in parentheses.
                    Always and only return JSON in the following format ```{json_form}```.
                    Ensure the JSON is properly formatted and does not contain any extra characters, malformed structures, and is properly encapsulated.
                    """
            },
            {
                "role": "user",
                "content": f"""Analyze the following job requirements and list key skills, qualifications, and experiences:\n\n{page_text}"""
            }
        ],
        max_tokens=4000,
        seed=42
    )

    retry_count = 0
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