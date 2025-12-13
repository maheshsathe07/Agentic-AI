# chain of thought
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# client = OpenAI(
#     api_key=GEMINI_API_KEY,
#     base_url="https://generativelanguage.googleapis.com/v1beta/"
# )

# DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
# client = OpenAI(
#     api_key=DEEPSEEK_API_KEY,
#     base_url="https://api.deepseek.com"
# )

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    
    return "Something went wrong"

available_tools = {
    "get_weather": get_weather
}

SYSTEM_PROMPT = """ 
    you're an expert AI Assistant in resolving user queries using chain of thought.
    you work on START, PLAN and OUTPUT steps.
    you need to first PLAN what needs to be done. The PLAN can be multiple steps.
    Once you think enough PLAN has been done, finally you can give an OUTPUT.
    You can also call a tool if required from the list of available tools.
    For every tool call wait for OBSERVE step which is the output from the called tool.

    Rules:
    - Strictly follow the given JSON output format.
    - Only run one step at a time.
    - The sequence of steps is START(user gives an input),
      PLAN(That can be multiple times),
      and finally OUTPUT(which is going to the displayed to the user).

    Output JSON Format:
    {"step": "START" | "PLAN" | "OUTPUT" | "TOOL", "content": "string", "tool": "string", "input": "string"}

    Available Tools:
    1. get_weather(city: str): Takes city name as input and returns the current weather information for that city.

    Example 1:
    START: Hey, can you solve 2 + 3 * 5 / 10?
    PLAN: {"step": "PLAN", "content": "Seems like user is interested in math problem"}
    PLAN: {"step": "PLAN", "content": "looking at the problem, we should solve this using BODMAS method"}
    PLAN: {"step": "PLAN", "content": "Yes, the BODMAS method is applicable here"}
    PLAN: {"step": "PLAN", "content": "first we must multiply 3 * 5 which is 15"}
    PLAN: {"step": "PLAN", "content": "Now new problem is 2 + 15 / 10"}
    PLAN: {"step": "PLAN", "content": "We must perform division that is 15/10 = 1.5"}
    PLAN: {"step": "PLAN", "content": "Now new problem is 2 + 1.5"}
    PLAN: {"step": "PLAN", "content": "Now finally we add 2 + 1.5 = 3.5"}
    PLAN: {"step": "PLAN", "content": "Great, we have solved and finally left with 3.5 as answer"}
    OUTPUT: {"step": "OUTPUT", "content": "3.5"}

    Example 2:
    START: What is the weather of Delhi?
    PLAN: {"step": "PLAN", "content": "Seems like user is interested in gettinhg weather information of Delhi in India"}
    PLAN: {"step": "PLAN", "content": "Lets see if we have any available tool from the list of available tools"}
    PLAN: {"step": "PLAN", "content": "Great, we have get_weather tool available for this query"}
    PLAN: {"step": "PLAN", "content": "i need to call get_weather tool for delhi as input for city"}
    PLAN: {"step": "TOOL", "tool": "get_weather", "input": "delhi"}
    PLAN: {"step": "OBSERVE", "tool": "get_weather", "output": "The temperature of delhi is cloudy with 20 degree celsius"}
    PLAN: {"step": "PLAN", "content": "Greate, i got the weather information for delhi"}
    OUTPUT: {"step": "OUTPUT", "content": "The current weather in delhi is 20 degree celsius with cloudy condition."}
"""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user","content": "Hey, write a code to add n numbers in js"}, # "content": "Hey, can you explain a+b whole square?"
        # as of now adding every step manually to the prompt, but later will automate this
        {"role": "assistant","content": json.dumps({"step": "START", "content": "You want a javascript code to add 'n' numbers"})},
        {"role": "assistant","content": json.dumps({"step": "PLAN", "content": "I need to write a JavaScript function that can add 'n' numbers."})},
        {"role": "assistant","content": json.dumps({"step": "PLAN", "content": "I will define a JavaScript function."})},
        {"role": "assistant","content": json.dumps({"step": "PLAN", "content": "The function should be able to accept an arbitrary number of arguments (n numbers)."})},
        {"role": "assistant","content": json.dumps({"step": "PLAN", "content": "I will use the rest parameter (...) to collect all passed numbers into an array."})},
        {"role": "assistant","content": json.dumps({"step": "PLAN", "content": "Inside the function, I will initialize a variable `sum` to 0."})},
        {"role": "assistant","content": json.dumps({"step": "PLAN", "content": "I will then iterate over this array of numbers, adding each number to the `sum`."})},
        {"role": "assistant","content": json.dumps({"step": "PLAN", "content": "Finally, I will return the `sum`."})}
    ],
    stream=False
)

print("\n\n\n")
message_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

while True:
    user_query = input("User: ")
    message_history.append({"role": "user","content": user_query})

    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=message_history
        )

        raw_response = response.choices[0].message.content
        message_history.append({"role": "assistant","content": raw_response})
        parsed_response = json.loads(raw_response)

        if parsed_response["step"] == "START":
            print("START: ", parsed_response.get("content"))
            continue

        elif parsed_response["step"] == "TOOL":
            tool_to_call = parsed_response.get("tool")
            tool_input = parsed_response.get("input")
            print("TOOL: ", {tool_to_call: tool_input})

            tool_response = available_tools[tool_to_call](tool_input)
            print(f"TOOL: , {tool_to_call} {tool_input} => {tool_response}")
            message_history.append({"role":"developer", "content": json.dumps(
                {"step":"OBSERVE", "tool":tool_to_call, "input":tool_input, "output":tool_response}
            )})
            continue

        elif parsed_response["step"] == "PLAN":
            print("PLAN: ", parsed_response.get("content"))
            continue    
        elif parsed_response["step"] == "OUTPUT":
            print("OUTPUT: ", parsed_response.get("content"))
            break
    print("\n\n\n")