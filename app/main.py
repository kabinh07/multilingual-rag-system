import os
import io
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from utils.graph import Graph
from utils.state import State
from utils.vector_db import VectorDB
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()
vector_db = VectorDB()
graph = Graph(vector_db).get_graph(save_png=True)
state = State(messages=[SystemMessage(content="You are an multilingual question answering assistant.")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify a list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "")
        state['messages'].append(HumanMessage(content=user_input))
        async def event_stream():
            logger.info(f"\n >>> State: {state}\n")
            for event, metadata in graph.stream(state, stream_mode="messages"):
                if event.content and event.type == "AIMessageChunk":
                    logger.info(event.content)
                    yield event.content
                if event.content and event.type == "ai":
                    state["messages"].append(AIMessage(content=event.content))
        return StreamingResponse(event_stream(), media_type="text/plain")
    except Exception as e:
        return {"error": str(e)}