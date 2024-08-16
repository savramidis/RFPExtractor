# RFP Extractor
Python-based Proof of Concept (POC) aimed at automating the process of matching employee profiles with staffing requirements specified in Requests for Proposals (RFPs). This solution leverages Azure's OpenAI GPT-4o model to intelligently analyze and align employee data with the key requirements outlined in the RFPs.

## Required for local .env
## Configuration Settings

### AZURE_STORAGE_CONNECTION_STRING
### AZURE_STORAGE_CONTAINER_NAME
### AZURE_STORAGE_FOLDER
### AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
### AZURE_DOCUMENT_INTELLIGENCE_KEY
### AZURE_OPENAI_API_KEY
### AZURE_OPENAI_ENDPOINT
### AZURE_OPENAI_DEPLOYMENT_NAME
### AZURE_COSMOS_ENDPOINT
### AZURE_COSMOS_KEY
### AZURE_COSMOS_DATABASE_NAME
### AZURE_COSMOS_CONTAINER_NAME
### LOCAL_RESUME_FOLDER

## Set Up
Set all your environment variables

pip install -r requirements.txt

## How to Run
### Step 1

- rfp_extractor.py
  - gets all files related to an RFP from an Azure Blob Storage folder and uses Azure Document Intelligence to parse the RFP files
  - staffing_requirements_extractor.py makes a call to Azure OpenAI with full RFP and prompt to extract staffing requirements
    - LLM result is stored in Cosmos DB with rfp_id as the partition key

### Step 2
- resume_creator.py
  - queries Cosmos DB for the LLM result from step 1
  - gets moq employee data
  - calls Azure OpenAI with prompt & data to generate a resume
  - data returned from the LLM is used to create a resume based on a template
