from fastapi import APIRouter,Request
import json
from app.services.init_thread import init_thread
# from app.checkpointer.check_pointer_singleton_factory import CheckpointerSingleton
from app.checkpointer.check_pointer_singleton_factory import CheckpointerSingleton

router = APIRouter()
@router.post("/init_thread")
async def create_thread(file_id: str):
    """
    Initialize a thread with the given file_id.
    """
    print(file_id)
    thread_id =await init_thread(file_id)
    print(thread_id)
    return {"thread_id": thread_id, "message": "Thread initialized successfully"}

#get all threads
@router.get("/get_threads")
async def get_threads():
    """
    Get all threads.
    """
    try:
        with open("app/storage/threads.json", "r") as f:
            threads = json.load(f)
    except FileNotFoundError:
        # If the file does not exist, return an empty list
        threads = []        
    except json.JSONDecodeError:
        # If the file is empty or not valid JSON, return an empty list
        threads = []

    return {"threads": threads}

#get thread data by thread_id from the checkpointer
@router.get("/get_thread/{thread_id}")
async def get_thread(thread_id: str):
    """
    Get thread data by thread_id.
    """
    config={
        "configurable":{
            "thread_id": thread_id,
           
        }
    }
    try:   
        checkpointer =CheckpointerSingleton.get()
        state =await checkpointer.aget(config)
        
        if state is None:
            return {"error": "Thread not found"}, 404
        return {"thread_id": thread_id, "state": state}
    except Exception as e:
        return {"error": str(e)}, 500

    