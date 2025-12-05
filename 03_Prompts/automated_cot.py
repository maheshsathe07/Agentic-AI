# chain of thought
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

SYSTEM_PROMPT = """ 
    you're an expert AI Assistant in resolving user queries using chain of thought.
    you work on START, PLAN and OUTPUT steps.
    you need to first PLAN what needs to be done. The PLAN can be multiple steps.
    Once you think enough PLAN has been done, finally you can give an OUTPUT.

    Rules:
    - Strictly follow the given JSON output format.
    - Only run one step at a time.
    - The sequence of steps is START(user gives an input),
      PLAN(That can be multiple times),
      and finally OUTPUT(which is going to the displayed to the user).

    Output JSON Format:
    {"step": "START" | "PLAN" | "OUTPUT", "content": "string"}

    Example:
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
"""
print("\n\n\n")
message_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

user_query = input("User: ")
message_history.append({"role": "user","content": user_query})

while True:
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        response_format={"type": "json_object"},
        messages=message_history
    )

    raw_response = response.choices[0].message.content
    message_history.append({"role": "assistant","content": raw_response})
    parsed_response = json.loads(raw_response)

    if parsed_response["step"] == "START":
        print("START: ", parsed_response.get("content"))
        continue
    elif parsed_response["step"] == "PLAN":
        print("PLAN: ", parsed_response.get("content"))
        continue    
    elif parsed_response["step"] == "OUTPUT":
        print("OUTPUT: ", parsed_response.get("content"))
        break
print("\n\n\n")

# with gemini it might not work that great, might give errors related to json parsing.