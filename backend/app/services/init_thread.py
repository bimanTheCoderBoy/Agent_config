import os
import json
import uuid
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from xml.etree import ElementTree as ET
import xmltodict
import json
from app.graph.state import GraphState, checkpointer  
import datetime

METADATA_DIR = "app/storage/metadata"
RAW_FILES_DIR="app/storage/raw_files"
THREADS_REGISTRY_PATH = "app/storage/threads.json"

def init_thread(file_id: str) -> str:
    # 1. get the metadata
    metadata_path = os.path.join(METADATA_DIR, f"{file_id}.json")
    if not os.path.exists(metadata_path):
        raise ValueError(f"Metadata for file_id {file_id} not found")
    
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    # 2. build a system message
    file_size = metadata.get('file_size', 0)
    if file_size <= 20000:
        raw_file_path = os.path.join(RAW_FILES_DIR, f"{file_id}.xml")
        with open(raw_file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
            file_content=xmltodict.parse(file_content)
            file_context=json.dumps(file_content, indent=2)
    else:
        file_context=( f"- File name: {metadata['original_filename']}\n"
            f"- Root tag: {metadata['root_tag']}\n"
            f"- Elements: {metadata['num_elements']}\n"
            f"- Top level tags: {', '.join(metadata['top_level_tags'])}\n"
            f"- Attribute keys: {', '.join(metadata['attribute_keys'])}\n"
            
            )
    system_context = ChatPromptTemplate.from_messages(
        [   
            ("system", """You are a helpful assistant that helps users to analize and understand Network file XML files.\n 
             do not answer questions that are not related to the file.
             if any question is asked that is not related to the file,
             you should respond with "I can only answer questions related to the file. Please ask a question related to the file."
             you will be provided the file data and metadata.
             """),
            ("system", f"File ID: {file_id}"),
            ("system", f"File content: {file_context}"),
           
           
            
        ]   
    ).invoke(
        file_id=file_id,
        file_context=file_context,
    )
    print(system_context)
    system_message = SystemMessage(content=system_context)

    # 3. create initial GraphState
    initial_state = GraphState(
        messages=[system_message]
    )

    # 4. generate thread_id
    thread_id = str(uuid.uuid4())

    # 5. store in the checkpointer
    checkpointer.put(thread_id, initial_state)

    if os.path.exists(THREADS_REGISTRY_PATH):
        with open(THREADS_REGISTRY_PATH, "r") as f:
            threads = json.load(f)
    else:
        threads = []

    # add new thread entry
    threads.append({
        "thread_id": thread_id,
        "file_id": file_id,
        "created_at": datetime.datetime.now().isoformat(),
      
    })

    # write back
    with open(THREADS_REGISTRY_PATH, "w") as f:
        json.dump(threads, f, indent=2)
    return thread_id
