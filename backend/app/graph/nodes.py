from app.graph.state import GraphState
from langgraph.graph import END
from langgraph.prebuilt import ToolNode
from app.graph.tools import retrieve_from_vectordb
from app.graph.tools import llm_with_bind_tools,llm
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import RoutingDecision
from langgraph.types import Command
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage,SystemMessage
from langchain.schema import messages_to_dict
    
def tools_router(state: GraphState):
    print("reach router")
    last_message = state.messages[-1]
    
    if(hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0):
        return "TOOL_NODE"
    else: 
        return END

async def llm_node(state:GraphState):
    print("reach llm")
    print(state)
    tool_message_count = sum(1 for msg in state.messages if isinstance(msg, ToolMessage))
    if tool_message_count>4:
        state.messages.append(SystemMessage(content="from now no more tool calls just summarize message and tell user the strat new thread limit reached for this thread"))
    message=await llm_with_bind_tools.ainvoke(state.messages)
    return {
        "messages":[message]
    }

tool_node=ToolNode(tools=[retrieve_from_vectordb])

async def llm_router(state:GraphState):
    print("llm router called")
    if state.is_startup is True:
        print("goto start up node")
        return Command(
            goto="STARTUP_NODE"
        )
   
    route_parser = PydanticOutputParser(pydantic_object=RoutingDecision)

    system_prompt = (
        "You are a routing agent that decides where the user query should go.  \n\n"
        "keep it in mind you are a RAG SYSTEM router, the RAG SYETEM work on Network Config XML or JSON file stored in vector db in chunks, so make the`refined_query` or `suggested_queries` for `retrieval` in that sense"
        "Types:\n"
        "- 'retrieval': user needs information from a file or vector store\n"
        "- 'normal': general conversation without retrieval\n\n"
        "If type is 'retrieval', fill `suggested_queries`.\n"
        "If type is 'normal', fill `refined_query`.\n\n"
   
        f"Format your response using:\n{route_parser.get_format_instructions().replace("{", "{{").replace("}", "}}")}"
    )
    
    input=state.user_query
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{input}")
    ])
    chain = prompt | llm.with_structured_output(RoutingDecision)
    print("llm router input  "+input)
    resp=await chain.ainvoke({"input":input})
    print(resp)
   
   
    if(resp.type=="retrieval"):
        print("going 02")
        updated_user_query=input+f"\n use tool call and your suggested queries are \n {resp.suggested_queries}"
        return Command(
            goto="LLM_NODE",
            # update={
            #     "user_query":updated_user_query,
            #     "messages":[HumanMessage(content=updated_user_query)]
            # }
        )
    elif(resp.type=="normal"):
        print("going 03")
        return Command(
            goto="LLM_NODE",
            # update={
            #     "user_query":resp.refined_query,
            #     "messages":[HumanMessage(content=resp.refined_query)]
            # }
        )
    
    
    
def startup_node(state:GraphState):
    print("start_up node")
    return {"messages":[AIMessage("Tell me how can I help you with the file ")], "is_startup":False}