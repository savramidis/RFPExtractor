# RFP Extractor
Simple POC that extracts staffing requirements from a Request from a Proposal and creates a resume from a template.

## Required for local .env
## Configuration Settings

### AZURE_STORAGE_CONNECTION_STRING
### AZURE_STORAGE_CONTAINER_NAME
### AZURE_STORAGE_FOLDER=<this is where the files for a single request for proposal are stored>
### AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
### AZURE_DOCUMENT_INTELLIGENCE_KEY
### AZURE_OPENAI_API_KEY
### AZURE_OPENAI_ENDPOINT
### AZURE_OPENAI_DEPLOYMENT_NAME
### AZURE_COSMOS_ENDPOINT
### AZURE_COSMOS_KEY
### AZURE_COSMOS_DATABASE_NAME
### AZURE_COSMOS_CONTAINER_NAME
### LOCAL_RESUME_FOLDER=<this is where the created resume will be saved>

## Set Up
Set all your environment variables

pip install -r requirements.txt

## How to Run
### Step 1

- rfp_extractor.py
  - gets RFPs from an Azure Blob Storage folder and uses Azure Document Intelligence to parse the RFP
  - staffing_requirements_extractor.py makes a call to an Azure OpenAI gpt-4o model with full RFP and prompt to extract staffing requirements
    - LLM result is stored in Cosmos DB

### Step 2
- resume_creator.py
  - queries Cosmos DB for the LLM result from step 1
  - gets moq employee data
  - calls a Azure OpenAI gpt-4o model with prompt & data to generate a resume
  - data returned from the LLM is used to create a resume based on a template
