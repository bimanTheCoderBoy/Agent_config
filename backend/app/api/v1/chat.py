from fastapi import APIRouter, Request, Query
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessageChunk
from app.graph.build import compiled_graph as graph
from langchain.schema import message_to_dict
import json

router = APIRouter()

def serialize_ai_message_chunk(chunk):
    if isinstance(chunk, AIMessageChunk):
        return chunk.content
    else:
        raise TypeError(
            f"Object of type {type(chunk).__name__} is not AIMessageChunk"
        )

@router.get("/chat")
async def chat(
    request: Request,
    query: str,
    thread_id: str 
):
    """
    SSE endpoint for chat streaming with vectorstore retrieval tool.
    """
    # Include file_id in the initial human message so the model can pick up
    # relevant context for retrieval
    human_message = HumanMessage(
        content=query,
    )
    inputs = {
        "user_query":query,
        "messages": [human_message],
        }
    config = {"configurable": {"thread_id": thread_id}}
    # response=await graph.ainvoke(input=inputs,config=config)
    async def generate_chat_events():
        async for event in graph.astream_events(inputs, version="v2", config=config):
            event_type = event["event"]
            if event_type == "on_chat_model_stream":
                chunk_content = serialize_ai_message_chunk(event["data"]["chunk"])
                safe_content = chunk_content.replace("\n", "\\n").replace('"', '\\"')
                yield f'data: {{"type": "content", "content": "{safe_content}"}}\n\n'

            elif event_type == "on_chat_model_end":
                # see if there is a tool call to the retriever
                tool_calls = getattr(event["data"]["output"], "tool_calls", [])
                retrieval_calls = [
                    call for call in tool_calls if call["name"] == "retrieve_from_vectordb"
                ]
                if retrieval_calls:
                    search_query = retrieval_calls[0]["args"].get("query", "")
                    safe_query = search_query.replace("\n", "\\n").replace('"', '\\"')
                    yield f'data: {{"type": "retrieval_start", "query": "{safe_query}"}}\n\n'

            elif event_type == "on_tool_end" and event.get("name") == "retrieve_from_vectordb":
                output = event["data"]["output"]
                print("\n\n\n tool output"+output.content)
                safe_content = json.dumps(output.content)
                yield f'data: {{"type": "retrieval_result", "content": {safe_content}}}\n\n'

        yield 'data: {"type": "end"}\n\n'

    return StreamingResponse(
        generate_chat_events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )
    # return response
