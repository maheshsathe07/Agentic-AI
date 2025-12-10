from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Optional, Literal
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
import os
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

openai_client = OpenAI()
groq_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

class State(TypedDict):
    user_query: str
    llm_output: Optional[str]
    is_good: Optional[bool]

def chatbot(state: State):
    print("ChatBot Node: ", state)
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": state.get("user_query")}
        ]
    )

    state['llm_output'] = response.choices[0].message.content
    return state

def evaluate_response(state: State) -> Literal["chatbot_gemini", "endnode"]:
    print("Evaluate Response Node: ", state)

    llm_output = state.get("llm_output") or ""
    user_query = state.get("user_query") or ""

    # Ask DeepSeek to evaluate if the answer is correct/helpful
    evaluation_prompt = f"""
    You are an evaluator. Check whether the following assistant response correctly
    and helpfully answers the user's query.

    USER QUERY:
    {user_query}

    ASSISTANT RESPONSE:
    {llm_output}

    Return ONLY one word:
    - "GOOD"  → if the assistant response is correct, helpful or acceptable
    - "BAD"   → if the answer is incorrect, incomplete, hallucinated or unhelpful
    """

    response = openai_client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a strict evaluator AI."},
            {"role": "user", "content": evaluation_prompt},
        ]
    )

    verdict = response.choices[0].message.content.strip().upper()
    print("Evaluator's verdict:", verdict)

    # Routing based on evaluation
    if verdict == "GOOD":
        return "endnode"
    else:
        return "chatbot_gemini"


def chatbot_gemini(state: State):
    print("ChatBot Gemini Node: ", state)
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": state.get("user_query")}
        ]
    )

    state['llm_output'] = response.choices[0].message.content
    return state

def endnode(state: State):
    print("Endnode Node: ", state)
    return state

graph_builder = StateGraph(State)

#node
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("chatbot_gemini", chatbot_gemini)
graph_builder.add_node("endnode", endnode)
graph_builder.add_node("evaluate_response", evaluate_response)

# edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", evaluate_response) # here need pass to node
graph_builder.add_edge("chatbot_gemini", "endnode")
graph_builder.add_edge("endnode", END)

graph = graph_builder.compile()

updated_state = graph.invoke(State({"user_query": "hey, what is 2 + 2"}))

print("updated-state: ", updated_state)