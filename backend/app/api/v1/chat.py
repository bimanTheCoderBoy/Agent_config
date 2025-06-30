from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from app.graph.build import graph_setup
router = APIRouter()

#route for chat stream response
@router.post("/chat")
async def chat(request: Request, query: str, thread_id: str):
    print(query)
    print(thread_id)
    async def event_generator():
            inputs = {
                "messages": [
                    HumanMessage(content=query)
                ],
                
            }
            config={
        "configurable":{
            "thread_id": thread_id,
           
        }
    }

            try:
                graph =await graph_setup()
                async for event in graph.astream_events(input=inputs,config=config,version="v2"):
                    print(event)
                    # if await request.is_disconnected():
                    #     break

                    # if event["event"] == "on_chat_model_stream":
                    #     # token = event["data"]["delta"]
                    #     yield f"data: {"jhgfd"}\n\n"

                    # if event["event"] == "on_node_end":
                    #     state = event["data"]["output"]
                    #     print(f"Updated state for thread {thread_id}: {state}")

            except Exception as e:
                print("Streaming error:", e)

            
    await event_generator()
    return {"data":"test"}