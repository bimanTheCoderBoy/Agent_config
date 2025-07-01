from langgraph.graph import StateGraph
from langchain.schema import BaseMessage
from app.graph.state import GraphState
from app.graph.nodes import llm_node, tool_node, tools_router, llm_router,startup_node
from langchain_core.messages import AIMessage
# from app.graph.state import checkpointer
from app.checkpointer.check_pointer_singleton_factory import CheckpointerSingleton
graph= StateGraph(GraphState)
LLM_NODE="LLM_NODE"
TOOL_NODE="TOOL_NODE"
TOOL_ROUTER="TOOL_ROUTER"
LLM_ROUTER="LLM_ROUTER"
STARTUP_NODE="STARTUP_NODE"

graph.add_node(LLM_ROUTER,llm_router)
graph.add_node(LLM_NODE,llm_node)
graph.add_node(TOOL_NODE,tool_node)
graph.add_node(STARTUP_NODE,startup_node)




graph.add_conditional_edges(LLM_NODE,tools_router)
graph.add_edge(TOOL_NODE,LLM_NODE)
graph.set_entry_point(LLM_ROUTER)

#cmpiled graph noe it can be invokable
# import aiosqlite
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
DB_PATH = "app/checkpointer/sqlite.db"

checkpointer = CheckpointerSingleton.get()
compiled_graph=graph.compile( checkpointer=checkpointer)

                




