from langgraph.graph import StateGraph
from langchain.schema import BaseMessage
from pydantic import BaseModel,Field
from typing import Any, Dict, Optional, Annotated,List
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


import operator
# import aiosqlite
DB_PATH = "app/checkpointer/sqlite.db"
VECTOR_DB_DIR = "app/storage/vector_db"
EMBEDDING_MODEL = "intfloat/e5-base-v2" 
MAX_CHUNK_SIZE = 500
MAX_CHUNK_OVERLAP = 100
class GraphState(BaseModel):
    """
    Represents the state of a graph.
    """
    id: str = Field(default_factory=lambda: "graph_state_1")
    messages:Annotated[List[BaseMessage], operator.add] = Field(default_factory=list)





embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device":"cpu"}
        )
        
        # create vector store
vectorstore = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings
        )

# checkpointer=None
# async def load_checkpointer_db():
#     global checkpointer
#     async with aiosqlite.connect(DB_PATH) as sqlite_conn:
#         app.state.checkpointer = AsyncSqliteSaver(sqlite_conn)
#         print("check pointer initialized")