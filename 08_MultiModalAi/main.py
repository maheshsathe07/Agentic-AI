from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {"role":"user", "content": [
            {"type":"text", "text":"Generate a caption for image in 50 words"},
            {"type":"image_url", "image_url":{"url":"https://images.pexels.com/photos/879109/pexels-photo-879109.jpeg"}}
        ]}
    ]
)

print(f"Response: {response.choices[0].message.content}")