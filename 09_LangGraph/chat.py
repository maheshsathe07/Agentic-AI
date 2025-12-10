from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages # this keeps on appending messages to the list
from langgraph.graph import StateGraph, START, END

# creating state
class State(TypedDict):
    messages: Annotated[list, add_messages]

# initially this list will have just one thing which is a user query
# whatever agent response that will get appended to this list

# node => it is accepting a state and modifying a state and then returning the state
def chatbot(state: State):
    print("\n\nInside ChatBot Node ", state)
    return {"messages": ["Hi, this is a message from ChatBot Node"]} # this will get appended to the messages list(state)

# state = {messages: ["Hello"]}
# node runs: chatbot(state: ["Hello"]) -> ["Hi, this is a message from ChatBot Node"]
# state = {messages: ["Hello", "Hi, this is a message from ChatBot Node"]}

def sampleNode(state: State):
    print("\n\nInside Sample Node ", state)
    return {"messages": ["Sample message appended"]} 

graph_builder = StateGraph(State)
# adding nodes
graph_builder.add_node("chatbot_node", chatbot)
graph_builder.add_node("sample_node", sampleNode)

# defining edges
graph_builder.add_edge(START, "chatbot_node")
graph_builder.add_edge("chatbot_node", "sample_node")
graph_builder.add_edge("sample_node", END)

# (START) -> chatbot_node -> sample_node -> (END)   

graph = graph_builder.compile()

updated_state = graph.invoke(State({"messages": ["Hello, my name is User"]}))

print("\n\nupdated_state: ", updated_state)