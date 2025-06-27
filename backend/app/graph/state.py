from langgraph.graph import StateGraph
from langchain.schema import BaseMessage
from pydantic import BaseModel,Field
from typing import Any, Dict, Optional, Annotated,List
from langgraph.checkpoint.sqlite import SqliteSaver
import operator
DB_PATH = "app/checkpointer/sqlite.db"

class GraphState(BaseModel):
    """
    Represents the state of a graph.
    """
    messages:Annotated[List[BaseMessage], operator.add] = Field(default_factory=list)



checkpointer = SqliteSaver.from_conn_string(f"sqlite:///{DB_PATH}")