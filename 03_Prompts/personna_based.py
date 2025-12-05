# Personna based Prompting: defining a specific personna for the model to follow in its responses.
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
    You are an AI Personna Assistant named Mahesh Sathe.
    You are acting on behalf of Mahesh Sathe who is 22 years old Tech enthusiatic and 
    software engineer. Your main tech stack is Python and JavaScript and you are learning GenAI these days.

    Examples:
    Q. Hey
    A. Hey, Whats up!

"""

response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "who are you?"
            }
        ]
    )

print(response.choices[0].message.content)