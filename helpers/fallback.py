import google.generativeai as genai
import os
import re

# Initialize Gemini API (put this near your other initializations)
def setup_gemini_api():
    try:
        api_key = os.getenv("GEMINI_API_KEY")  # Store your API key as an environment variable
        if not api_key:
            st.warning("Gemini API key not found. Fallback to Gemini will not be available.")
            return False
            
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.warning(f"Could not initialize Gemini API: {str(e)}")
        return False

# Function to use Gemini for equation extraction
def extract_latex_with_gemini(image_path):
    try:
        # Load the image
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
        
        # Set up the model
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # Create the prompt
        prompt = "Convert this mathematical equation to LaTeX. Provide only the LaTeX code without any explanation or markdown formatting."
        
        # Generate content
        response = model.generate_content(
            [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
        )
        
        # Extract the LaTeX
        latex_result = response.text.strip()
        
        # Clean up the result (remove markdown formatting if present)
        if latex_result.startswith("```latex") and latex_result.endswith("```"):
            latex_result = latex_result[8:-3].strip()
        elif latex_result.startswith("```") and latex_result.endswith("```"):
            latex_result = latex_result[3:-3].strip()
            
        return latex_result
        
    except Exception as e:
        st.error(f"Error using Gemini API: {str(e)}")
        return None