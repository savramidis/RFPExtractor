# RFP Extractor


## Required for local .env
## Configuration Settings

### AZURE_STORAGE_CONNECTION_STRING
Connection string for Azure storage account. This string is used to authenticate and connect to your Azure storage account.

### AZURE_STORAGE_CONTAINER_NAME
Name of the Azure storage container. This is the container within your Azure storage account where your data will be stored.

### AZURE_STORAGE_FOLDER
Folder path within the Azure storage container. Specify the folder structure within the storage container for organizing your data.

### AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
Endpoint URL for Azure Document Intelligence service. This is the URL used to access the Document Intelligence service provided by Azure.

### AZURE_DOCUMENT_INTELLIGENCE_KEY
API key for Azure Document Intelligence service. This key is used to authenticate requests to the Document Intelligence service.

### AZURE_OPENAI_API_KEY
API key for Azure OpenAI service. This key is used to authenticate requests to the OpenAI services provided by Azure.

### AZURE_OPENAI_ENDPOINT
Endpoint URL for Azure OpenAI service. This is the URL used to access the OpenAI services provided by Azure.

### AZURE_OPENAI_DEPLOYMENT_NAME
Deployment name for Azure OpenAI service. This is the specific deployment of the OpenAI service that you are using within Azure.

### AZURE_COSMOS_ENDPOINT
Endpoint URL for Azure Cosmos DB service. This is the URL used to access the Cosmos DB service provided by Azure.

### AZURE_COSMOS_KEY
API key

## How to Run
Set all your environment variables

pip install -r requirements.txt

rfp_extractor.py reads from an Azure Blob Storage folder and uses Azure Document Intelligence to parse the RFP.

staffing_requirements_extractor.py uses the extracted data and calls Azure Open AI to extract staffing requirements and then stores that output in Cosmos DB.

