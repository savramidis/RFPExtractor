# RFP Extractor
Python-based Proof of Concept (POC) aimed at automating the process of matching employee profiles with staffing requirements specified in Requests for Proposals (RFPs). This solution leverages Azure's OpenAI GPT-4o model to intelligently analyze and align employee data with the key requirements outlined in the RFPs.

# Key Functionality
## Extraction of Key Staffing Information

The POC begins by parsing and extracting critical staffing information from RFP documents. This includes identifying specific roles, qualifications, skills, experience levels, and other pertinent criteria that are essential for fulfilling the proposal’s requirements.

## Employee Data Integration

Comprehensive employment data, including employee profiles, qualifications, work history, and skill sets, is then integrated into the system. This data serves as the basis for matching against the RFP requirements.

## AI-Powered Matching

The extracted staffing requirements and the full set of employee data are passed to Azure's OpenAI GPT-4o model. The model utilizes its natural language processing (NLP) capabilities to understand and match the employee profiles with the RFP criteria. This includes assessing not just direct matches, but also identifying potential fits based on transferable skills, related experience, and other nuanced factors.

## Output and Recommendations

The system generates a list of recommended employees who best align with the RFP requirements. These recommendations can include a ranking or scoring of candidates based on how well their profiles meet the specified criteria, providing decision-makers with clear insights into the optimal staffing choices for the proposal.

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

### Step 1: Extract RFP and Staffing Requirements

- **rfp_extractor.py**:
  - Retrieves all RFP-related files from an Azure Blob Storage folder.
  - Uses Azure Document Intelligence to parse these files.

- **staffing_requirements_extractor.py**:
  - Sends the full RFP and a prompt to Azure OpenAI to extract staffing requirements.
  - Stores the extracted data in Cosmos DB, using `rfp_id` as the partition key.

### Step 2: Generate Resumes

- **resume_creator.py**:
  - Queries Cosmos DB for the extracted staffing requirements.
  - Retrieves mock employee data.
  - Sends a prompt and data to Azure OpenAI to generate a resume.
  - Uses the LLM-generated data to create a resume based on a template.

