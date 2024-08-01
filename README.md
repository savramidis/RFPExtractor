# RFP Extractor


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

## How to Run
Set all your environment variables

pip install -r requirements.txt

rfp_extractor.py reads from an Azure Blob Storage folder and uses Azure Document Intelligence to parse the RFP.

staffing_requirements_extractor.py uses the extracted data and calls Azure Open AI to extract staffing requirements and then stores that output in Cosmos DB.
