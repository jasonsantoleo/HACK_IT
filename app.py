import streamlit as st
from pix2tex.cli import LatexOCR
from PIL import Image
import google.generativeai as genai
import io
import time

# Page Configuration
st.set_page_config(
    page_title="Math Equation Solver",
    page_icon="📝",
    layout="wide"
)

# Initialize session state variables
if "latex_model" not in st.session_state:
    st.session_state.latex_model = None
if "latex_code" not in st.session_state:
    st.session_state.latex_code = ""
if "history" not in st.session_state:
    st.session_state.history = []

# Function to initialize the LatexOCR model
def load_latex_model():
    try:
        with st.spinner("Loading OCR model (this may take a moment)..."):
            st.session_state.latex_model = LatexOCR()
        return True
    except Exception as e:
        st.error(f"Failed to load LaTeX OCR model: {str(e)}")
        return False

# Function to configure Gemini API
def configure_gemini_api(api_key):
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        st.error(f"Failed to configure Gemini API: {str(e)}")
        return None

# Function to process image and extract LaTeX
def process_image(image):
    try:
        if st.session_state.latex_model is None:
            if not load_latex_model():
                return None
        
        # Extract LaTeX from image
        latex_code = st.session_state.latex_model(image)
        st.session_state.latex_code = latex_code
        return latex_code
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

# Function to get response from Gemini
def get_gemini_response(prompt, gemini_model):
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error getting response from Gemini: {str(e)}")
        return None

# Main application
def main():
    # Title and description
    st.title("📝 Math Equation Solver & Assistant")
    
    # Sidebar for API configuration
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Gemini API Key", value="AIzaSyB5K90gSeNAxULBv1xp4xhy6PK0bXiMgeI", type="password")
        st.caption("Your API key is securely stored in this session only.")
        
        if st.button("Initialize Models"):
            gemini_model = configure_gemini_api(api_key)
            if gemini_model and load_latex_model():
                st.success("✅ Models loaded successfully!")
        
        st.divider()
        st.markdown("### How to use")
        st.markdown("""
        1. Enter your Gemini API key
        2. Initialize the models
        3. Upload an image with a math equation
        4. Review the extracted LaTeX
        5. Get solutions and explanations
        6. Ask follow-up questions
        """)

    # Create two columns for the main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Equation Image")
        uploaded_file = st.file_uploader("Select image file (JPG, PNG, JPEG)", type=["jpg", "png", "jpeg"])
        
        if uploaded_file:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Process button
            if st.button("Process Equation"):
                with st.spinner("Processing image..."):
                    gemini_model = configure_gemini_api(api_key)
                    if gemini_model:
                        latex_code = process_image(image)
                        
                        if latex_code:
                            st.success("Equation extracted successfully!")
                            st.session_state.history = []  # Reset history with new equation
                        else:
                            st.error("Could not extract equation. Please try a clearer image.")
    
    with col2:
        if st.session_state.latex_code:
            st.subheader("Extracted LaTeX")
            st.code(st.session_state.latex_code, language="latex")
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["Solution", "Step-by-Step", "Ask Questions"])
            
            gemini_model = configure_gemini_api(api_key)
            if not gemini_model:
                st.error("Please initialize the models first")
                return
            
            with tab1:
                if st.button("Get Solution", key="solution_button"):
                    with st.spinner("Solving..."):
                        solution_prompt = f"Solve this equation and provide the final numerical or algebraic answer: {st.session_state.latex_code}"
                        solution = get_gemini_response(solution_prompt, gemini_model)
                        if solution:
                            st.markdown("### Solution")
                            st.markdown(solution)
            
            with tab2:
                if st.button("Get Explanation", key="explanation_button"):
                    with st.spinner("Generating explanation..."):
                        explanation_prompt = f"Explain step by step how to solve this equation: {st.session_state.latex_code}"
                        explanation = get_gemini_response(explanation_prompt, gemini_model)
                        if explanation:
                            st.markdown("### Step-by-Step Explanation")
                            st.markdown(explanation)
            
            with tab3:
                st.markdown("### Ask Follow-up Questions")
                user_question = st.text_input("Type your question about this equation:")
                
                if user_question:
                    if st.button("Submit Question"):
                        with st.spinner("Generating answer..."):
                            # Add question to history
                            st.session_state.history.append({"role": "user", "content": user_question})
                            
                            # Generate contextualized prompt
                            context_prompt = f"""
                            Answer the user's question related to this equation: {st.session_state.latex_code}
                            User's question: {user_question}
                            Provide a clear, educational response with examples if necessary.
                            """
                            
                            response = get_gemini_response(context_prompt, gemini_model)
                            if response:
                                st.session_state.history.append({"role": "assistant", "content": response})
                
                # Display conversation history
                st.divider()
                st.markdown("### Conversation History")
                for message in st.session_state.history:
                    if message["role"] == "user":
                        st.markdown(f"**You:** {message['content']}")
                    else:
                        st.markdown(f"**Assistant:** {message['content']}")
                        st.divider()

# Run the application
if __name__ == "__main__":
    main()
# import streamlit as st
# import os
# import numpy as np
# from config import Config
# from helpers.image_helper import create_temp_file, preprocess_handwritten_image
# from PIL import Image
# from pix2tex.cli import LatexOCR
# import google.generativeai as genai

# # Initialize the Pix2Tex model
# # This might take a moment on first run as it downloads the model
# @st.cache_resource
# def load_ocr_model():
#     st.write("Loading LaTeX OCR model (this may take a moment on first run)...")
#     model = LatexOCR()
#     st.write("LaTeX OCR model loaded successfully!")
#     return model

# # Initialize Gemini API
# @st.cache_resource
# def initialize_gemini_api():
#     try:
#         # Get API key from environment variable or Streamlit secrets
#         # IMPORTANT: In production, use st.secrets or environment variables instead of hardcoding
#         api_key = os.environ.get('GEMINI_API_KEY')
#         if not api_key:
#             # For development only - remove this in production
#             api_key = 'AIzaSyACjpm3eVYgPgJ19dqdT5084dS5XySHgyU'
#             os.environ['GEMINI_API_KEY'] = api_key
            
#         genai.configure(api_key=api_key)
#         return True
#     except Exception as e:
#         st.error(f"Error initializing Gemini API: {str(e)}")
#         return None

# # Function to query Gemini with LaTeX
# def query_gemini(latex_string, query_type="explain"):
#     try:
#         # Configure the model
#         generation_config = {
#             "temperature": 0.7,
#             "top_p": 0.95,
#             "top_k": 0,
#             "max_output_tokens": 2048,
#         }
        
#         # Select model - using gemini-1.5-flash instead of gemini-pro
#         model = genai.GenerativeModel(
#             model_name="gemini-1.5-flash",
#             generation_config=generation_config
#         )
        
#         # Prepare prompts based on query type
#         prompts = {
#             "explain": f"Explain the following mathematical expression in detail: {latex_string}",
#             "solve": f"Solve the following mathematical equation and show your work: {latex_string}",
#             "simplify": f"Simplify the following mathematical expression and show your work: {latex_string}",
#             "applications": f"Explain real-world applications of the following mathematical concept: {latex_string}"
#         }
        
#         prompt = prompts.get(query_type, prompts["explain"])
        
#         # Generate the response
#         response = model.generate_content(prompt)
#         return response.text
        
#     except Exception as e:
#         return f"Error querying Gemini API: {str(e)}"

# # Function to extract LaTeX from image
# def extract_latex(image_path, model, apply_preprocessing=True):
#     try:
#         img = Image.open(image_path)
        
#         if apply_preprocessing:
#             # Apply handwriting-optimized preprocessing
#             processed_img = preprocess_handwritten_image(img)
#             # Save processed image for debugging
#             processed_path = image_path + "_processed.jpg"
#             processed_img.save(processed_path)
#         else:
#             processed_img = img
#             # Convert to grayscale if needed
#             if processed_img.mode != 'L':
#                 processed_img = processed_img.convert('L')
        
#         # Perform OCR
#         latex_string = model(processed_img)
#         return latex_string, processed_img
#     except Exception as e:
#         st.error(f"Error extracting equation: {str(e)}")
#         return None, None

# # Page configuration
# page_title = Config.PAGE_TITLE
# st.set_page_config(
#     page_title=page_title,
#     initial_sidebar_state="expanded",
# )

# # Page title
# st.title(page_title)
# st.markdown("#### Select an Image to convert to LaTeX and analyze with Gemini 1.5 Flash")

# # Load the OCR model
# model = load_ocr_model()

# # Initialize Gemini API
# gemini_available = initialize_gemini_api()

# # Create session state to store results between reruns
# if 'latex_result' not in st.session_state:
#     st.session_state.latex_result = None
# if 'processed_img' not in st.session_state:
#     st.session_state.processed_img = None
# if 'gemini_response' not in st.session_state:
#     st.session_state.gemini_response = None

# # File uploader widget
# uploaded_file = st.file_uploader("Choose image file", type=['png', 'jpg', 'jpeg'])

# # Add options for processing handwritten equations
# preprocessing_options = st.expander("Advanced Options")
# with preprocessing_options:
#     apply_preprocessing = st.checkbox("Apply handwriting optimization", value=True)
#     st.write("Enable this for handwritten equations to improve recognition")

# if uploaded_file is None:
#     st.info("You must select an image file to convert!")
#     # Add demo section
#     st.subheader("About this app")
#     st.write("""
#     This app extracts LaTeX equations from images and uses Google's Gemini 1.5 Flash AI to analyze them.
    
#     **Features:**
#     - Convert handwritten or printed equations to LaTeX
#     - Solve equations
#     - Explain mathematical concepts
#     - Find real-world applications
#     - Simplify expressions
    
#     Upload an image to get started!
#     """)
#     st.stop()

# if uploaded_file:
#     # Display the uploaded image
#     st.write(f"✅ Uploaded file: {uploaded_file.name}, Type: {uploaded_file.type}")
#     st.image(uploaded_file, caption="Original Image", use_container_width=True)
    
#     # Create a button to process with Pix2Tex
#     latex_col1, latex_col2 = st.columns([2, 1])
#     with latex_col1:
#         convert_button = st.button("Convert to LaTeX", key="convert_latex_button", use_container_width=True)

#     if convert_button:
#         # Processing message
#         with st.status("Processing image file. DON'T LEAVE THIS PAGE WHILE IMAGE IS BEING CONVERTED...."):
#             st.write("Converting Image to LaTeX ....")
            
#             # Save the uploaded file temporarily
#             temp_file_path = create_temp_file(uploaded_file)
            
#             # Extract LaTeX using Pix2Tex
#             latex_result, processed_img = extract_latex(
#                 temp_file_path, 
#                 model,
#                 apply_preprocessing=apply_preprocessing
#             )
            
#             # Store in session state to persist between reruns
#             st.session_state.latex_result = latex_result
#             st.session_state.processed_img = processed_img
            
#             if latex_result:
#                 st.write("✅ Done converting image to LaTeX")
#             else:
#                 st.error("Failed to convert image to LaTeX")
#                 st.session_state.latex_result = "Conversion failed. Please try another image."
    
#     # Display results if available
#     if st.session_state.latex_result:
#         # Show the processed image if preprocessing was applied
#         if apply_preprocessing and st.session_state.processed_img is not None:
#             st.subheader("Processed Image:")
#             st.image(st.session_state.processed_img, caption="Processed for OCR", use_container_width=True)
            
#         # Display LaTeX result
#         st.subheader("LaTeX Result:")
#         latex_area = st.text_area("LaTeX Code", st.session_state.latex_result, height=200, key="latex_area")
        
#         # Show rendered LaTeX
#         try:
#             st.subheader("Rendered LaTeX:")
#             st.latex(latex_area)
#         except Exception as e:
#             st.error(f"Could not render LaTeX: {str(e)}")
        
#         # Option to download LaTeX
#         st.download_button(
#             label="Download LaTeX",
#             data=latex_area,
#             file_name="latex_result.tex",
#             mime="text/plain",
#             key="download_latex"
#         )
        
#         # Option to edit and regenerate
#         st.subheader("Edit LaTeX if needed:")
#         edited_latex = st.text_area("Edit LaTeX", latex_area, height=150, key="edited_latex_area")
        
#         if edited_latex != latex_area:
#             update_col1, update_col2 = st.columns([2, 1])
#             with update_col1:
#                 if st.button("Update Rendered LaTeX", key="update_latex_button", use_container_width=True):
#                     st.subheader("Updated Rendered LaTeX:")
#                     try:
#                         st.latex(edited_latex)
#                     except Exception as e:
#                         st.error(f"Could not render edited LaTeX: {str(e)}")
                    
#                     # Update download button with edited content
#                     st.download_button(
#                         label="Download Edited LaTeX",
#                         data=edited_latex,
#                         file_name="edited_latex_result.tex",
#                         mime="text/plain",
#                         key="download_edited_latex"
#                     )
        
#         # Gemini Integration Section
#         if gemini_available:
#             st.header("Analyze with Gemini 1.5 Flash")
            
#             # Use a form to prevent page refresh issues
#             with st.form(key="gemini_query_form"):
#                 # Select query type
#                 query_type = st.selectbox(
#                     "What would you like Gemini to do with this equation?",
#                     ["explain", "solve", "simplify", "applications"],
#                     key="query_type_select"
#                 )
                
#                 # Create form submit button
#                 submit_gemini = st.form_submit_button("Ask Gemini", use_container_width=True)
            
#             # Process form submission outside the form to avoid nested form issues
#             if submit_gemini:
#                 with st.status("Querying Gemini AI..."):
#                     # Use either edited or original LaTeX
#                     final_latex = edited_latex if edited_latex != latex_area else latex_area
                    
#                     # Query Gemini
#                     gemini_response = query_gemini(final_latex, query_type)
#                     st.session_state.gemini_response = gemini_response
            
#             # Display Gemini's response if available
#             if st.session_state.gemini_response:
#                 st.subheader(f"Gemini {query_type.capitalize()} Response:")
#                 st.markdown(st.session_state.gemini_response)
                
#                 # Option to download Gemini's response
#                 st.download_button(
#                     label="Download Gemini Analysis",
#                     data=st.session_state.gemini_response,
#                     file_name=f"gemini_{query_type}_analysis.md",
#                     mime="text/markdown",
#                     key="download_gemini_response"
#                 )
#         else:
#             st.warning("Gemini AI integration is not available. Please check your API key configuration.")
# import streamlit as st
# import os
# import numpy as np
# from config import Config
# from helpers.image_helper import create_temp_file, preprocess_handwritten_image
# from PIL import Image
# from pix2tex.cli import LatexOCR
# import google.generativeai as genai

# # Initialize the Pix2Tex model
# # This might take a moment on first run as it downloads the model
# @st.cache_resource
# def load_ocr_model():
#     st.write("Loading LaTeX OCR model (this may take a moment on first run)...")
#     model = LatexOCR()
#     st.write("LaTeX OCR model loaded successfully!")
#     return model

# # Initialize Gemini API
# @st.cache_resource
# def initialize_gemini_api():
#     try:
#         # Get API key from environment variable or Streamlit secrets
#         os.environ['GEMINI_API_KEY'] = 'AIzaSyACjpm3eVYgPgJ19dqdT5084dS5XySHgyU'
#         api_key = os.environ.get('GEMINI_API_KEY')
#         if not api_key:
#             st.warning("Gemini API key not found. Please add it to environment variables or Streamlit secrets.")
#             return None
            
#         genai.configure(api_key=api_key)
#         return True
#     except Exception as e:
#         st.error(f"Error initializing Gemini API: {str(e)}")
#         return None

# # Function to query Gemini with LaTeX
# def query_gemini(latex_string, query_type="explain"):
#     try:
#         # Configure the model
#         generation_config = {
#             "temperature": 0.7,
#             "top_p": 0.95,
#             "top_k": 0,
#             "max_output_tokens": 2048,
#         }
        
#         # Select model
#         model = genai.GenerativeModel(
#             model_name="gemini-pro",
#             generation_config=generation_config
#         )
        
#         # Prepare prompts based on query type
#         prompts = {
#             "explain": f"Explain the following mathematical expression in detail: {latex_string}",
#             "solve": f"Solve the following mathematical equation and show your work: {latex_string}",
#             "simplify": f"Simplify the following mathematical expression and show your work: {latex_string}",
#             "applications": f"Explain real-world applications of the following mathematical concept: {latex_string}"
#         }
        
#         prompt = prompts.get(query_type, prompts["explain"])
        
#         # Generate the response
#         response = model.generate_content(prompt)
#         return response.text
        
#     except Exception as e:
#         return f"Error querying Gemini API: {str(e)}"

# # Function to extract LaTeX from image
# def extract_latex(image_path, model, apply_preprocessing=True):
#     try:
#         img = Image.open(image_path)
        
#         if apply_preprocessing:
#             # Apply handwriting-optimized preprocessing
#             processed_img = preprocess_handwritten_image(img)
#             # Save processed image for debugging
#             processed_path = image_path + "_processed.jpg"
#             processed_img.save(processed_path)
#         else:
#             processed_img = img
#             # Convert to grayscale if needed
#             if processed_img.mode != 'L':
#                 processed_img = processed_img.convert('L')
        
#         # Perform OCR
#         latex_string = model(processed_img)
#         return latex_string, processed_img
#     except Exception as e:
#         st.error(f"Error extracting equation: {str(e)}")
#         return None, None

# # Page configuration
# page_title = Config.PAGE_TITLE
# st.set_page_config(
#     page_title=page_title,
#     initial_sidebar_state="expanded",
# )

# # Page title
# st.title(page_title)
# st.markdown("#### Select an Image to convert to LaTeX and analyze with Gemini")

# # Load the OCR model
# model = load_ocr_model()

# # Initialize Gemini API
# gemini_available = initialize_gemini_api()

# # File uploader widget
# uploaded_file = st.file_uploader("Choose image file", type=['png', 'jpg', 'jpeg'])

# # Add options for processing handwritten equations
# preprocessing_options = st.expander("Advanced Options")
# with preprocessing_options:
#     apply_preprocessing = st.checkbox("Apply handwriting optimization", value=True)
#     st.write("Enable this for handwritten equations to improve recognition")

# if uploaded_file is None:
#     st.info("You must select an image file to convert!")
#     # Add demo section
#     st.subheader("About this app")
#     st.write("""
#     This app extracts LaTeX equations from images and uses Google's Gemini AI to analyze them.
    
#     **Features:**
#     - Convert handwritten or printed equations to LaTeX
#     - Solve equations
#     - Explain mathematical concepts
#     - Find real-world applications
#     - Simplify expressions
    
#     Upload an image to get started!
#     """)
#     st.stop()

# if uploaded_file:
#     # Display the uploaded image
#     st.write(f"✅ Uploaded file: {uploaded_file.name}, Type: {uploaded_file.type}")
#     st.image(uploaded_file, caption="Original Image", use_column_width=True)
    
#     # Create a button to process with Pix2Tex
#     if st.button("Convert to LaTeX"):
#         # Processing message
#         with st.status("Processing image file. DON'T LEAVE THIS PAGE WHILE IMAGE IS BEING CONVERTED...."):
#             st.write("Converting Image to LaTeX ....")
            
#             # Save the uploaded file temporarily
#             temp_file_path = create_temp_file(uploaded_file)
            
#             # Extract LaTeX using Pix2Tex
#             latex_result, processed_img = extract_latex(
#                 temp_file_path, 
#                 model,
#                 apply_preprocessing=apply_preprocessing
#             )
            
#             if latex_result:
#                 st.write("✅ Done converting image to LaTeX")
                
#                 # Show the processed image if preprocessing was applied
#                 if apply_preprocessing and processed_img is not None:
#                     st.subheader("Processed Image:")
#                     st.image(processed_img, caption="Processed for OCR", use_column_width=True)
#             else:
#                 st.error("Failed to convert image to LaTeX")
#                 latex_result = "Conversion failed. Please try another image."
        
#         # Display LaTeX result
#         st.subheader("LaTeX Result:")
#         latex_area = st.text_area("LaTeX Code", latex_result, height=200)
        
#         # Show rendered LaTeX
#         try:
#             st.subheader("Rendered LaTeX:")
#             st.latex(latex_result)
#         except Exception as e:
#             st.error(f"Could not render LaTeX: {str(e)}")
        
#         # Option to download LaTeX
#         st.download_button(
#             label="Download LaTeX",
#             data=latex_result,
#             file_name="latex_result.tex",
#             mime="text/plain",
#         )
        
#         # Option to edit and regenerate
#         st.subheader("Edit LaTeX if needed:")
#         edited_latex = st.text_area("Edit LaTeX", latex_result, height=150)
        
#         if edited_latex != latex_result:
#             if st.button("Update Rendered LaTeX"):
#                 st.subheader("Updated Rendered LaTeX:")
#                 try:
#                     st.latex(edited_latex)
#                 except Exception as e:
#                     st.error(f"Could not render edited LaTeX: {str(e)}")
                
#                 # Update download button with edited content
#                 st.download_button(
#                     label="Download Edited LaTeX",
#                     data=edited_latex,
#                     file_name="edited_latex_result.tex",
#                     mime="text/plain",
#                 )
        
#         # Gemini Integration Section
#         if gemini_available:
#             st.header("Analyze with Gemini AI")
            
#             # Select query type
#             query_type = st.selectbox(
#                 "What would you like Gemini to do with this equation?",
#                 ["explain", "solve", "simplify", "applications"]
#             )
            
#             # Create button to send to Gemini
#             if st.button("Ask Gemini"):
#                 with st.status("Querying Gemini AI..."):
#                     # Use either edited or original LaTeX
#                     final_latex = edited_latex if edited_latex != latex_result else latex_result
                    
#                     # Query Gemini
#                     gemini_response = query_gemini(final_latex, query_type)
                
#                 # Display Gemini's response
#                 st.subheader(f"Gemini {query_type.capitalize()} Response:")
#                 st.markdown(gemini_response)
                
#                 # Option to download Gemini's response
#                 st.download_button(
#                     label="Download Gemini Analysis",
#                     data=gemini_response,
#                     file_name=f"gemini_{query_type}_analysis.md",
#                     mime="text/markdown",
#                 )
#         else:
#             st.warning("Gemini AI integration is not available. Please check your API key configuration.")
# import streamlit as st
# import os
# import numpy as np
# from config import Config
# from helpers.image_helper import create_temp_file, preprocess_handwritten_image
# from PIL import Image
# from pix2tex.cli import LatexOCR

# # Initialize the Pix2Tex model
# # This might take a moment on first run as it downloads the model
# @st.cache_resource
# def load_ocr_model():
#     st.write("Loading LaTeX OCR model (this may take a moment on first run)...")
#     model = LatexOCR()
#     st.write("LaTeX OCR model loaded successfully!")
#     return model

# # Function to extract LaTeX from image
# def extract_latex(image_path, model, apply_preprocessing=True):
#     try:
#         img = Image.open(image_path)
        
#         if apply_preprocessing:
#             # Apply handwriting-optimized preprocessing
#             processed_img = preprocess_handwritten_image(img)
#             # Save processed image for debugging
#             processed_path = image_path + "_processed.jpg"
#             processed_img.save(processed_path)
#         else:
#             processed_img = img
#             # Convert to grayscale if needed
#             if processed_img.mode != 'L':
#                 processed_img = processed_img.convert('L')
        
#         # Perform OCR
#         latex_string = model(processed_img)
#         return latex_string, processed_img
#     except Exception as e:
#         st.error(f"Error extracting equation: {str(e)}")
#         return None, None

# # Page configuration
# page_title = Config.PAGE_TITLE
# st.set_page_config(
#     page_title=page_title,
#     initial_sidebar_state="expanded",
# )

# # Page title
# st.title(page_title)
# st.markdown("#### Select an Image to convert to LaTeX.")

# # Load the OCR model
# model = load_ocr_model()

# # File uploader widget
# uploaded_file = st.file_uploader("Choose image file", type=['png', 'jpg', 'jpeg'])

# # Add options for processing handwritten equations
# preprocessing_options = st.expander("Advanced Options")
# with preprocessing_options:
#     apply_preprocessing = st.checkbox("Apply handwriting optimization", value=True)
#     st.write("Enable this for handwritten equations to improve recognition")

# if uploaded_file is None:
#     st.error("You must select an image file to convert!")
#     st.stop()

# if uploaded_file:
#     # Display the uploaded image
#     st.write(f"✅ Uploaded file: {uploaded_file.name}, Type: {uploaded_file.type}")
#     st.image(uploaded_file, caption="Original Image", use_column_width=True)
    
#     # Create a button to process with Pix2Tex
#     if st.button("Convert to LaTeX"):
#         # Processing message
#         with st.status("Processing image file. DON'T LEAVE THIS PAGE WHILE IMAGE IS BEING CONVERTED...."):
#             st.write("Converting Image to LaTeX ....")
            
#             # Save the uploaded file temporarily
#             temp_file_path = create_temp_file(uploaded_file)
            
#             # Extract LaTeX using Pix2Tex
#             latex_result, processed_img = extract_latex(
#                 temp_file_path, 
#                 model,
#                 apply_preprocessing=apply_preprocessing
#             )
            
#             if latex_result:
#                 st.write("✅ Done converting image to LaTeX")
                
#                 # Show the processed image if preprocessing was applied
#                 if apply_preprocessing and processed_img is not None:
#                     st.subheader("Processed Image:")
#                     st.image(processed_img, caption="Processed for OCR", use_column_width=True)
#             else:
#                 st.error("Failed to convert image to LaTeX")
#                 latex_result = "Conversion failed. Please try another image."
        
#         # Display LaTeX result
#         st.subheader("LaTeX Result:")
#         latex_area = st.text_area("LaTeX Code", latex_result, height=200)
        
#         # Show rendered LaTeX
#         try:
#             st.subheader("Rendered LaTeX:")
#             st.latex(latex_result)
#         except Exception as e:
#             st.error(f"Could not render LaTeX: {str(e)}")
        
#         # Option to download LaTeX
#         st.download_button(
#             label="Download LaTeX",
#             data=latex_result,
#             file_name="latex_result.tex",
#             mime="text/plain",
#         )
        
#         # Option to edit and regenerate
#         st.subheader("Edit LaTeX if needed:")
#         edited_latex = st.text_area("Edit LaTeX", latex_result, height=150)
        
#         if edited_latex != latex_result:
#             if st.button("Update Rendered LaTeX"):
#                 st.subheader("Updated Rendered LaTeX:")
#                 try:
#                     st.latex(edited_latex)
#                 except Exception as e:
#                     st.error(f"Could not render edited LaTeX: {str(e)}")
                
#                 # Update download button with edited content
#                 st.download_button(
#                     label="Download Edited LaTeX",
#                     data=edited_latex,
#                     file_name="edited_latex_result.tex",
#                     mime="text/plain",
#                 )
# import streamlit as st
# import os
# from config import Config
# from helpers.image_helper import create_temp_file
# from PIL import Image
# from pix2tex.cli import LatexOCR

# # Initialize the Pix2Tex model
# # This might take a moment on first run as it downloads the model
# @st.cache_resource
# def load_ocr_model():
#     st.write("Loading LaTeX OCR model (this may take a moment on first run)...")
#     model = LatexOCR()
#     st.write("LaTeX OCR model loaded successfully!")
#     return model

# # Function to extract LaTeX from image
# def extract_latex(image_path, model):
#     try:
#         img = Image.open(image_path)
#         # Convert to grayscale if needed
#         if img.mode != 'L':
#             img = img.convert('L')
#         # Perform OCR
#         latex_string = model(img)
#         return latex_string
#     except Exception as e:
#         st.error(f"Error extracting equation: {str(e)}")
#         return None

# # Page configuration
# page_title = Config.PAGE_TITLE
# st.set_page_config(
#     page_title=page_title,
#     initial_sidebar_state="expanded",
# )

# # Page title
# st.title(page_title)
# st.markdown("#### Select an Image to convert to LaTeX.")

# # Load the OCR model
# model = load_ocr_model()

# # File uploader widget
# uploaded_file = st.file_uploader("Choose image file", type=['png', 'jpg', 'jpeg'])
# if uploaded_file is None:
#     st.error("You must select an image file to convert!")
#     st.stop()

# if uploaded_file:
#     # Display the uploaded image
#     st.write(f"✅ Uploaded file: {uploaded_file.name}, Type: {uploaded_file.type}")
#     st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
#     # Create a button to process with Pix2Tex
#     if st.button("Convert to LaTeX"):
#         # Processing message
#         with st.status("Processing image file. DON'T LEAVE THIS PAGE WHILE IMAGE IS BEING CONVERTED...."):
#             st.write("Converting Image to LaTeX ....")
            
#             # Save the uploaded file temporarily
#             temp_file_path = create_temp_file(uploaded_file)
            
#             # Extract LaTeX using Pix2Tex
#             latex_result = extract_latex(temp_file_path, model)
            
#             if latex_result:
#                 st.write("✅ Done converting image to LaTeX")
#             else:
#                 st.error("Failed to convert image to LaTeX")
#                 latex_result = "Conversion failed. Please try another image."
                
#         # Display LaTeX result
#         st.subheader("LaTeX Result:")
#         latex_area = st.text_area("LaTeX Code", latex_result, height=300)
        
#         # Show rendered LaTeX
#         st.subheader("Rendered LaTeX:")
#         st.latex(latex_result)
        
#         # Option to download LaTeX
#         st.download_button(
#             label="Download LaTeX",
#             data=latex_result,
#             file_name="latex_result.tex",
#             mime="text/plain",
#         )
        
#         # Option to edit and regenerate
#         st.subheader("Edit LaTeX if needed:")
#         edited_latex = st.text_area("Edit LaTeX", latex_result, height=200)
#         if edited_latex != latex_result:
#             if st.button("Update Rendered LaTeX"):
#                 st.subheader("Updated Rendered LaTeX:")
#                 st.latex(edited_latex)
#                 # Update download button with edited content
#                 st.download_button(
#                     label="Download Edited LaTeX",
#                     data=edited_latex,
#                     file_name="edited_latex_result.tex",
#                     mime="text/plain",
#                 )