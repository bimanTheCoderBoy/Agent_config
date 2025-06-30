from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from app.graph.build import compiled_graph as graph
import json
import asyncio

router = APIRouter()

@router.get("/chat", response_class=StreamingResponse)
async def chat(request: Request, query: str, thread_id: str):
    """
    Streams back Server-Sent Events (SSE) for a LangGraph chat.
    Query parameters:
      - query: the user’s message
      - thread_id: ID for LangGraph conversation state
    """
    async def event_generator():
        # Build your inputs and config for LangGraph
        inputs = {"messages": [HumanMessage(content=query)]}
        config = {"configurable": {"thread_id": thread_id}}

        try:
            # Iterate over LangGraph streaming events
            async for event in graph.astream_events(input=inputs, config=config, version="v2"):
                # If client has disconnected, stop producing events
                if await request.is_disconnected():
                    print("Client disconnected, stopping event stream.")
                    break

                ev_type = event.get("event")
                data = event.get("data", {})

                if ev_type == "on_chat_model_stream":
                    # This event will carry incremental tokens
                    token = data.get("delta", "")
                    # SSE: just send the data payload
                    yield f"data: {json.dumps({'token': token})}\n\n"

                elif ev_type == "on_node_end":
                    # This event signals that the node has completed
                    yield "event: done\ndata: {}\n\n"

                else:
                    # For any other events, wrap generically
                    yield f"event: {ev_type}\ndata: {json.dumps(data)}\n\n"

            # When the generator finishes cleanly, send a final done event
            yield "event: done\ndata: {}\n\n"

        except Exception as e:
            # On errors, send an SSE error event
            err = {"error": str(e)}
            yield f"event: error\ndata: {json.dumps(err)}\n\n"
            print("Streaming error:", e)

    # Return the streaming response with the proper media type
    return StreamingResponse(event_generator(), media_type="text/event-stream")
