import os
import json
import uuid
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from xml.etree import ElementTree as ET
import xmltodict
import json
from app.graph.state import GraphState  
import datetime
from app.graph.build import compiled_graph

# from app.checkpointer.check_pointer_singleton_factory import CheckpointerSingleton

METADATA_DIR = "app/storage/metadata"
RAW_FILES_DIR="app/storage/raw_files"
THREADS_REGISTRY_PATH = "app/storage/threads.json"

async def init_thread(file_id: str) -> str:
    # 1. get the metadata
    metadata_path = os.path.join(METADATA_DIR, f"{file_id}.json")
    if not os.path.exists(metadata_path):
        raise ValueError(f"Metadata for file_id {file_id} not found")
    
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    # 2. build a system message
    file_size = metadata.get('size', 0)
    
    if file_size <= 20000:
        raw_file_path = os.path.join(RAW_FILES_DIR, f"{file_id}.xml")
        with open(raw_file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
            file_content=xmltodict.parse(file_content)
            file_context=json.dumps(file_content, indent=2)
    else:
        file_context=( f"- File name: {metadata['file_name']}\n"
            f"- Root tag: {metadata['root_tag']}\n"
            f"- Elements: {metadata['num_elements']}\n"
            f"- Top level tags: {', '.join(metadata['top_level_tags'])}\n"
            f"- Attribute keys: {', '.join(metadata['attribute_keys'])}\n"
            f"- File id: {', '.join(metadata['file_id'])}\n"
            )
    system_context = SystemMessage(
            content = f"""You are a helpful assistant that helps users to analyze and understand Network XML configuration files files.
        Do not answer questions that are not related to the file.
        If any unrelated question is asked, respond with:
        "I can only answer questions related to the file. Please ask a question related to the file."
        you the user query need retriver call then make some retriver query based the conversation and user query and use the file id={file_id} for make the tool calls 
        File ID: {file_id}

        File content or metadata:
        {file_context}
        """
        )

    # print(system_context)
    
    thread_id = str(uuid.uuid4())
    # 3. create initial GraphState
    initial_state = GraphState(
        user_query="",
        id=thread_id,
        messages=[system_context,SystemMessage(content="Now first greet the user")],
        file_id=file_id,
        is_startup=True
    )
   
    # 4. generate thread_id
    

    # 5. store in the checkpointer
    config={
        "configurable":{
            "thread_id": thread_id,
            "checkpoint_ns":""
        }
    }
#     checkpointer=CheckpointerSingleton.get()
#     # checkpointer=CheckpointerSingleton.get()
#     checkpoint = {
#   "v": 1,
#   "id": initial_state.id,
#   "ts": datetime.datetime.utcnow().isoformat() + "Z",
#   "channel_values": {
#   },
#   "channel_versions": {"count": 1, "messages": 1},
#   "messages":initial_state.dict()["messages"],
#   "versions_seen": {},
#   "pending_sends": []
# }
#     test=  await checkpointer.aput(config,checkpoint, new_versions={}, metadata={})
#     print(test)

    await compiled_graph.ainvoke(initial_state,config=config)
    
    #------------for future---------now just in memory
    # if os.path.exists(THREADS_REGISTRY_PATH):
    #     with open(THREADS_REGISTRY_PATH, "r") as f:
    #         threads = json.load(f)
    # else:
    #     threads = []

    # add new thread entry
    # threads.append({
    #     "thread_id": thread_id,
    #     "file_id": file_id,
    #     "file_name": metadata.get('file_name', 'Unknown'),
    #     "created_at": datetime.datetime.now().isoformat(),
      
    # })

    # # write back
    # with open(THREADS_REGISTRY_PATH, "w") as f:
    #     json.dump(threads, f, indent=2)
    return thread_id
