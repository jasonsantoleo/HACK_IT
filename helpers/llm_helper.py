"""
DevTechBytes
https://www.youtube.com/@DevTechBytes
"""
import streamlit as st

from ollama import generate
from config import Config
from helpers.image_helper import get_image_bytes



system_prompt = Config.SYSTEM_PROMPT

response = generate(model="llava:7b", prompt="Describe the image...")
def analyze_image_file(image_file, model, user_prompt):
    #gets image bytes using helper function 
    image_bytes = get_image_bytes(image_file)

    #Calls the llava model using Ollama SDK
    stream = generate(model = model.strip(),
                      prompt = user_prompt,
                      images = [image_bytes],
                      stream = True)
    st.write(f"Selected Model: {model}")  # Debugging print

    return stream   

# handles stream response back from LLM
def stream_parser(stream):
    for chunk in stream:
        yield chunk['response']