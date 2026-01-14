import os
import uuid

def driver_document_path(instance, filename):

    ext = filename.split('.')[-1] 
    random_name = uuid.uuid4().hex  
    return os.path.join("driver_documents", f"{random_name}.{ext}")
