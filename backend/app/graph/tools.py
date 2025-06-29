from langchain_core.tools import tool
from app.graph.state import vectorstore
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()
@tool
def retrieve_from_vectordb(query:str, file_id:str):
    """Use this tool for retrieve chuncks from the vector db related to the XML file user is working on
    Args:
        query (str): query for finding the similarity search
        file_id (str): file id of the file working on need for filtering the search
    """
    docs= vectorstore.similarity_search(query=query,filter={"file_id":file_id}, k=5)
    return "".join(doc for doc in docs)

llm= ChatGroq(model="llama-3.1-8b-instant")
llm_with_bind_tools=llm.bind_tools([retrieve_from_vectordb])