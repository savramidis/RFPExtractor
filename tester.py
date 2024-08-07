# Anything you want to test goes herefrom cosmos_db_service import cosmos_db_service
import uuid
from cosmos_db_service import cosmos_db_service
from datetime import datetime, timezone

rfp_id = str(uuid.uuid4())
currentDate = str(datetime.now(timezone.utc))
id = str(uuid.uuid4())

single_document = {
            "id": id,
            "rfp_id": rfp_id,
            "doc_type": "rfp_staffing_extract",
            "extract_date": currentDate,
            "status": "rfp_extracted",
            "blob_name": "doc.pdf",
            "rfp_staffing_requirements": "TEST1"
        }

cosmos_db_service = cosmos_db_service()
cosmos_db_service.initialize()
created_item = cosmos_db_service.insert_rfp_staffing_extract(single_document)
print(created_item)

updated_item = cosmos_db_service.update_rfp_staffing_extract(id, rfp_id, "status", "resume_created")
print(updated_item)