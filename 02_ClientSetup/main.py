from openai import OpenAI
from dotenv import load_dotenv
import os
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

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    n=1,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Explain to me how AI works. Give in 2 lines."
        }
    ]
)

print(response.choices[0].message.content)