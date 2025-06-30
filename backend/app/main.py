from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.checkpointer.check_pointer_singleton_factory import CheckpointerSingleton





    

app = FastAPI(
    title="Config AI Backend",
    description="Upload XML → Parse → QA",
    version="1.0.0",
    
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
@app.on_event("startup")
async def startup():
    await CheckpointerSingleton.initialize()
    
    from app.api.v1 import upload,get_files, thread,chat
    app.include_router(upload.router, prefix="/api/v1")
    app.include_router(get_files.router, prefix="/api/v1")
    app.include_router(thread.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")

# app.include_router(analysis.router, prefix="/api/v1")
# app.include_router(qa.router, prefix="/api/v1")
 