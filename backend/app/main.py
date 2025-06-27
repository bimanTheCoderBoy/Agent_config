from fastapi import FastAPI
from app.api.v1 import upload,get_files, thread


app = FastAPI(
    title="Config AI Backend",
    description="Upload XML → Parse → QA",
    version="1.0.0"
)

app.include_router(upload.router, prefix="/api/v1")
app.include_router(get_files.router, prefix="/api/v1")
app.include_router(thread.router, prefix="/api/v1")
# app.include_router(analysis.router, prefix="/api/v1")
# app.include_router(qa.router, prefix="/api/v1")
