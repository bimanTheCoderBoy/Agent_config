from fastapi import APIRouter
import os
import json
router = APIRouter()

METADATA_DIR = "app/storage/metadata"

@router.get("/get_files")
async def get_files():
    """
    Endpoint to retrieve a list of uploaded files.
    """
    list_of_files = []
    try:
        # List all files in the metadata directory
        for filename in os.listdir(METADATA_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(METADATA_DIR, filename), 'r', encoding="utf-8") as file:
                    metadata = json.load(file)
                    list_of_files.append(metadata)
    except FileNotFoundError:
        return {"message": "Metadata directory not found."}
    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}
    return {"message": "successfully retrieved files", "files": list_of_files}