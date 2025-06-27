from langgraph.graph import StateGraph
from langchain.schema import BaseMessage
from pydantic import BaseModel,Field
from typing import Any, Dict, Optional, Annotated,List
from langgraph.checkpoint.sqlite import SqliteSaver
import operator
import sqlite3
DB_PATH = "app/checkpointer/sqlite.db"

class GraphState(BaseModel):
    """
    Represents the state of a graph.
    """
    id: str = Field(default_factory=lambda: "graph_state_1")
    messages:Annotated[List[BaseMessage], operator.add] = Field(default_factory=list)


sqlite_conn = sqlite3.connect(DB_PATH,check_same_thread=False)
checkpointer = SqliteSaver(sqlite_conn)