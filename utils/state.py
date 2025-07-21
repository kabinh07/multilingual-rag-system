from typing import Annotated, List, TypedDict
from operator import add
from langchain_core.messages import AnyMessage

class State(TypedDict):
    messages: Annotated[List[AnyMessage], add]