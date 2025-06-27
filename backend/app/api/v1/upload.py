from fastapi import APIRouter, File, UploadFile
import os

from app.services.file_loader import load_file

router = APIRouter()

UPLOAD_DIR = "app/data"

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    await load_file(file)
    return {"filename": file.filename, "message": "File uploaded successfully"}
