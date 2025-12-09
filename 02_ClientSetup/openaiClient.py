from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

client = OpenAI()

response = client.responses.create(
    model="gpt-5-nano",
    input="Write a short bedtime story about a unicorn."
)

print(response.output_text)
