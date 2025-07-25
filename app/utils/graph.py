import io
import os
import json
from PIL import Image
from langgraph.graph import StateGraph
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from utils.state import State
from utils.vector_db import VectorDB
from utils.utils import clean_full_text
from config import LLM_MODEL, OLLAMA_BASE_URL, LLM_TEMP, STOPWORD_PATH
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Graph:
    def __init__(self, vector_db: VectorDB):
        self.llm = ChatOllama(model=LLM_MODEL, temperature=LLM_TEMP, base_url=OLLAMA_BASE_URL)
        self.vector_db = vector_db
        self.stop_words = self.__get_stop_words(lang="bn")
        self.prompt = PromptTemplate(
            input_variables=["context", "query"],
            template="""
            Your task is to answer user's questions based on the context provided.

            # Rule:
            - If the result is a single character (e.g. "ক", "খ", "গ", etc.), which means it's a mcq answer, then search the context for the answer. 
            - **Response in the language of the user** and the as short as possible.
            - No need to say about the context if the user doesn't ask.
            - If the context is blank, response with "Not in my knowledge base".

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
    
    def __get_stop_words(self, lang="bn"):
        with open(os.path.join(STOPWORD_PATH, f"{lang}.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    
    def __retrieve_context(self, query: str, k=10):
        new_query = [word for word in query.split(" ") if word not in self.stop_words]
        query = " ".join(new_query)
        query = clean_full_text(query)
        logger.info(f"\n\nRetrieving context for query: {query}\n\n")
        docs = self.vector_db.vector_store.similarity_search(query, k=k)
        logger.info(f"\n\nRetrieved:\n{"\n".join([doc.page_content for doc in docs])}\n\n")
        return "\n".join([doc.page_content for doc in docs])

    def chatbot(self, state: State) -> State:
        user_messages = state["messages"].copy()
        context = self.__retrieve_context(user_messages[-1].content)
        user_messages[-1] = HumanMessage(content=self.prompt.format(context=context, query=user_messages[-1].content))
        logger.info(f"LLM: {self.llm}")
        response = self.llm.invoke(user_messages)
        state["messages"].append(AIMessage(content=response.content, tool_calls=getattr(response, "tool_calls", [])))
        return state