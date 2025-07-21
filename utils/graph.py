import io
from PIL import Image
from langgraph.graph import StateGraph
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from utils.state import State
from utils.vector_db import VectorDB
from config import LLM_MODEL, OLLAMA_BASE_URL, LLM_TEMP
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Graph:
    def __init__(self, vector_db: VectorDB):
        self.llm = ChatOllama(model=LLM_MODEL, temperature=LLM_TEMP, base_url=OLLAMA_BASE_URL)
        self.vector_db = vector_db
        self.prompt = PromptTemplate(
            input_variables=["context", "query"],
            template="""
            You are an multilingual question answering assistant.

            # Rule:
            - No need to say about the context if the user doesn't ask.
            - If the context is blank, response with "Not in my knowledge base".
            - Response in the language of the user.

            Here is some context:
            {context}

            Based on this, answer the user's question:
            {query}
            """
            )
        
    def get_graph(self, save_png=False):
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.set_entry_point("chatbot")
        graph_builder.set_finish_point("chatbot")
        graph =graph_builder.compile()

        if save_png:
            png_bytes = graph.get_graph().draw_mermaid_png()
            image = Image.open(io.BytesIO(png_bytes))
            image.save("graph.png")

        return graph
    
    def __retrieve_context(self, query: str, k=3):
        docs = self.vector_db.vector_store.similarity_search(query, k=k)
        return "\n".join([doc.page_content for doc in docs])

    def chatbot(self, state: State) -> State:
        user_messages = state["messages"].copy()
        context = self.__retrieve_context(user_messages[-1].content)
        user_messages[-1] = HumanMessage(content=self.prompt.format(context=context, query=user_messages[-1].content))
        logger.info(f"LLM: {self.llm}")
        response = self.llm.invoke(user_messages)
        state["messages"].append(AIMessage(content=response.content, tool_calls=getattr(response, "tool_calls", [])))
        return state