# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("text-generation", model="nvidia/Nemotron-Orchestrator-8B")
messages = [
    {"role": "user", "content": "Who are you?"},
]
pipe(messages)