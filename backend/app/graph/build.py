from langgraph.graph import StateGraph
from langchain.schema import BaseMessage
from app.graph.state import GraphState
from app.graph.nodes import llm_node, tool_node, tools_router
from langchain_core.messages import AIMessage
# from app.graph.state import checkpointer
from app.checkpointer.check_pointer_singleton_factory import CheckpointerSingleton
graph= StateGraph(GraphState)
LLM_NODE="llm_node"
TOOL_NODE="tool_node"
TOOL_ROUTER="tool_router"

graph.add_node(LLM_NODE,llm_node)
graph.add_node(TOOL_NODE,tool_node)


graph.add_conditional_edges(LLM_NODE,tools_router)
graph.add_edge(TOOL_NODE,LLM_NODE)
graph.set_entry_point(LLM_NODE)

#cmpiled graph noe it can be invokable
# import aiosqlite
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
DB_PATH = "app/checkpointer/sqlite.db"

checkpointer = CheckpointerSingleton.get()
compiled_graph=graph.compile( checkpointer=checkpointer)

startup_graph=StateGraph(GraphState)
def startup_node(state):
    return {"messages":[AIMessage("Tell me how can I help you")]}
startup_graph.add_node("STARTUP",startup_node)
startup_graph.set_entry_point("STARTUP")
compiled_startup_graph=startup_graph.compile(checkpointer=checkpointer)
                




