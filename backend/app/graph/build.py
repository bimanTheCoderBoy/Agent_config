from langgraph.graph import StateGraph
from langchain.schema import BaseMessage
from app.graph.state import GraphState
from app.graph.nodes import llm_node, tool_node, tools_router
from app.graph.state import checkpointer
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
compiled_graph=graph.compile( checkpointer=checkpointer)




