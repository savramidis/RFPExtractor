# Anything you want to test goes herefrom cosmos_db_service import cosmos_db_service
import uuid
from cosmos_db_service import cosmos_db_service
from datetime import datetime, timezone

rfp_id = str(uuid.uuid4())
currentDate = str(datetime.now(timezone.utc))

first_document = {
            "id": str(uuid.uuid4()),
            "rfp_id": rfp_id,
            "doc_type": "rfp_staffing_extract",
            "extract_date": currentDate,
            "status": "rfp_extracted",
            "blob_name": "doc1.pdf",
            "rfp_staffing_requirements": "TEST1"
        }

second_document = {
            "id": str(uuid.uuid4()),
            "rfp_id": rfp_id,
            "doc_type": "rfp_staffing_extract",
            "extract_date": currentDate,
            "status": "rfp_extracted",
            "blob_name": "doc2.pdf",
            "rfp_staffing_requirements": "TEST2"
        }

third_document = {
            "id": str(uuid.uuid4()),
            "rfp_id": rfp_id,
            "doc_type": "employee_data",
            "extract_date": currentDate
        }

cosmos_db_service = cosmos_db_service()
cosmos_db_service.initialize()
created_item = cosmos_db_service.insert_rfp_staffing_extract(first_document)
print(created_item)

created_item = cosmos_db_service.insert_rfp_staffing_extract(second_document)
print(created_item)

created_item = cosmos_db_service.insert_rfp_staffing_extract(third_document)
print(created_item)

items = cosmos_db_service.get_all_by_rfp_id(rfp_id)

for item in items:
    print(item)