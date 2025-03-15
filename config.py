"""
DevTechBytes
https://www.youtube.com/@DevTechBytes
"""
class Config:
    PAGE_TITLE = "LLava Image Analyzer"
# OLLAMA_MODELS = ('llava:v1.6', 'llava:13b', 'backllava')

    OLLAMA_MODELS = ('llava:latest','llama2:latest','llava:7b  ')
    SYSTEM_PROMPT = f"""You are a helpful chatbot that has access to the following open-source vision models {OLLAMA_MODELS}. You can answer questions about images."""
    