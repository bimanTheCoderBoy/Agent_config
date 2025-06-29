from app.graph.state import GraphState
from langgraph.graph import END
from langgraph.prebuilt import ToolNode
from app.graph.tools import retrieve_from_vectordb
from app.graph.tools import llm_with_bind_tools
    
def tools_router(state: GraphState):
    last_message = state.messages[-1]

    if(hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0):
        return "tool_node"
    else: 
        return END

def llm_node(state:GraphState):
    message=llm_with_bind_tools.invoke(state.messages)
    return {
        "messages":[message]
    }

tool_node=ToolNode(tools=[retrieve_from_vectordb])
    
