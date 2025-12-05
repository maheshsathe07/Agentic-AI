# Few Shot Prompting: providing a few examples in the prompt to guide the model's responses.
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

# Zero Shot Prompting: directly giving instructions(in the prompt) to the model with few examples
SYSTEM_PROMPT = """You should only and only answer the coding related questions in a concise manner.
   Do not answer anything else. Your name is Alexa. If user asks something other than coding,
   reply with 'I am sorry, I can only answer coding related questions.
   
   Rules:
   - Strictly follow the output in JSON format.

   Output Format:
   {{
   "code": string (the code snippet),
   "isCodingQuestion": boolean (true if the question is coding related, false otherwise)
   }}

   examples:
   Q. Can you tell me a joke?
   A. {{"code":null, "isCodingQuestion": false}}

    Q. How to reverse a list in python?
    A. {{"code":"You can reverse a list in python using the reverse() method or slicing.", "isCodingQuestion": true}}

    Q. Write a python code for adding two numbers.
    A. {{"code":"def add(a, b):
          return a + b", "isCodingQuestion": true}}
   """
response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            # "content": "Hey, can you explain a+b whole square?"
            "content": "Hey, write a code to add n numbers in js"
        }
    ]
)

print(response.choices[0].message.content)