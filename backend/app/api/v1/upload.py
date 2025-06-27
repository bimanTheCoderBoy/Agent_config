from fastapi import APIRouter, File, UploadFile
import os

router = APIRouter()

UPLOAD_DIR = "app/data"

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename, "message": "File uploaded successfully"}
