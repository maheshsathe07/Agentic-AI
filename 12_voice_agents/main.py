import asyncio
import speech_recognition as sr
from openai import OpenAI
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

async_client = AsyncOpenAI()

async def tts(speech: str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        instructions="Always speak in cheerful manner with full of delight and happy",
        input=speech,
        response_format="pcm"
    ) as response:
        await LocalAudioPlayer().play(response)

def main():
    r = sr.Recognizer() # Speech To Text

    with sr.Microphone() as source: # mic access
        r.adjust_for_ambient_noise(source) # cutting background noises
        r.pause_threshold=2 # if user stops for 2 seconds we will start with llm

        SYSTEM_PROMPT = f"""
            You're an expert voice agent. You are given the transcript of what user has said using voice.
            You need to output as if you are an voice agent and whatever you speak will be converted back 
            to audio using AI and played back to server.
        """

        messages = [
             {"role":"system", "content":SYSTEM_PROMPT}
        ]

        while True:
            print("Speak Something...")
            audio = r.listen(source)

            print("Processing Audio...(STT)")
            try:
                stt = r.recognize_google(audio)
            except sr.UnknownValueError:
                print("Didn't catch that, no speech detected. Exiting loop...")
                break
            except sr.RequestError as e:
                print(f"STT request error: {e}")
                break

            print("You said: ", stt)

            messages.append({"role":"user", "content":stt})

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages
            )

            llm_response = response.choices[0].message.content
            print("BOT: ", llm_response)
            asyncio.run(tts(speech=llm_response))

main()