from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages # this keeps on appending messages to the list
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langgraph.checkpoint.mongodb import MongoDBSaver

load_dotenv()

llm = init_chat_model(
    model='gpt-5-nano',
    model_provider='openai'
)
# creating state
class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    response = llm.invoke(state.get("messages"))
    return {"messages": [response]} 

graph_builder = StateGraph(State)
# adding nodes
graph_builder.add_node("chatbot_node", chatbot)

# defining edges
graph_builder.add_edge(START, "chatbot_node")
graph_builder.add_edge("chatbot_node", END) 

# graph = graph_builder.compile()

def compile_graph_with_checkpoint(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

DB_URI = "mongodb://admin:admin@localhost:27017"
with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
    graph_with_checkpointer = compile_graph_with_checkpoint(checkpointer)

    config = {
        "configurable":{
            "thread_id":"Mahesh" # with this thread it stores history in mongodb, changing this context will get changes means it preserves history as per thread id.
        }
    }
    for chunk in graph_with_checkpointer.stream(
        State({"messages": ["Hello, what is my name?"]}),
        config=config,
        stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()


# all the history is getting saved in mongodb, thus it maintains previous chat history.