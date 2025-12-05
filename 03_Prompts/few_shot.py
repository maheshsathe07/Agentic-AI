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
   
   examples:
   Q. Can you tell me a joke?
   A. I am sorry, I can only answer coding related questions.

    Q. How to reverse a list in python?
    A. You can reverse a list in python using the reverse() method or slicing.

    Q. Write a python code for adding two numbers.
    A. def(a, b):
        return a + b
   """
response = client.chat.completions.create(
    model="gemini-2.5-flash",
    n=1,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            # "content": "Hey, can you tell me a joke?" => will be ignored by the model
            "content": "Hey, can you write a python code to translate the word hello to hindi."
        }
    ]
)

print(response.choices[0].message.content)