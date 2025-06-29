import os
import uuid
import json
from fastapi import UploadFile
from xml.etree import ElementTree as ET
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveJsonSplitter
from langchain.schema import Document
import xmltodict
from langchain_huggingface import HuggingFaceEmbeddings
from app.graph.state import vectorstore
UPLOAD_DIR = "app/storage/raw_files"
METADATA_DIR = "app/storage/metadata"
VECTOR_DB_DIR = "app/storage/vector_db"
EMBEDDING_MODEL = "intfloat/e5-base-v2" 
MAX_CHUNK_SIZE = 500
MAX_CHUNK_OVERLAP = 100

async def load_file(file: UploadFile):
    file_id= str(uuid.uuid4())
    file_content= await file.read()
    #upload raw files
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file_id+".xml")
    with open(file_path, "wb") as f:
        f.write(file_content)
        
        
    # set metadata
    extracted_metadata=extract_xml_metadata(file_path)
    metadata = {
        "file_id": file_id,
        "file_name": file.filename,
        "file_path": file_path,
        "file_type": file.content_type,
        "size": os.path.getsize(file_path),
        **extracted_metadata
    }
    # save metadata
    metadata_path = os.path.join(METADATA_DIR, file_id + ".json")
    os.makedirs(METADATA_DIR, exist_ok=True)
    with open(metadata_path, "w") as meta_file:
        json.dump(metadata, meta_file, indent=4)
    
    
    # load and store to vector store
    await load_and_store_to_vector_store(file, file_content, metadata)
    


def extract_xml_metadata(file_path):
    """
    Parse XML and extract helpful metadata
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # root tag
        root_tag = root.tag

        # top-level tags
        top_level_tags = [child.tag for child in root]

        # attribute keys
        attribute_keys = []
        for elem in root.iter():
            for attr in elem.attrib.keys():
                attribute_keys.append(attr)
        attribute_keys = list(set(attribute_keys))

        # num elements
        num_elements = len(list(root.iter()))

        return {
            "root_tag": root_tag,
            "top_level_tags": top_level_tags,
            "attribute_keys": attribute_keys,
            "num_elements": num_elements,
            
        }
    except Exception as e:
        raise Exception(f"Error parsing XML: {e}")
    
    
async def load_and_store_to_vector_store(file: UploadFile, file_content, metadata: dict):
    """
    Load XML file, split text, and store in vector store
    """
    try:
        #conver to json for more efficient storing
        dist_file= xmltodict.parse(file_content)
        # json_data = json.dumps(dist_file, indent=4)
        
        # chucks using RecursiveJsonSplitter
        splitter=RecursiveJsonSplitter( max_chunk_size=MAX_CHUNK_SIZE)
        chunks = splitter.split_json(dist_file)
        docs=[]
        for ind, chunk in enumerate(chunks):
            doc = Document(
                page_content=json.dumps(chunk, indent=4),
                metadata={
                    "file_id": metadata["file_id"],
                    "file_name": metadata["file_name"],
                    "file_type": metadata["file_type"],
                    "chunk_index": ind
                }
            )
            docs.append(doc)
        

        vectorstore.add_documents(docs)
        

        print(f"Stored {len(docs)} chunks in Chroma for file_id: {metadata["file_id"]}")
        

    except Exception as e:
        raise Exception(f"Error loading and storing to vector store: {e}")