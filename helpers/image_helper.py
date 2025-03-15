import io
import tempfile
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import streamlit as st

def create_temp_file(text_file):
    """
    Creates a temporary file from an uploaded file and returns the path.
    Args:
    text_file: The file uploaded through Streamlit
    Returns:
    str: Path to the temporary file
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(text_file.getbuffer())
        return temp_file.name

def get_image_bytes(image_file):
    """
    Converts an image file to bytes for API transmission.
    Args:
    image_file: The image file to convert
    Returns:
    bytes: The image converted to bytes
    """
    if image_file is None:
        raise ValueError("❌ No image file was uploaded!")
    
    # Open the image file
    image = Image.open(image_file)
    
    # Convert the image to bytes
    image_bytes = io.BytesIO()
    image.save(image_bytes, format=image.format or "JPEG")
    return image_bytes.getvalue()

def preprocess_handwritten_image(img):
    """
    Optimize handwritten image for better OCR results
    Args:
    img: PIL Image object
    Returns:
    PIL Image: Processed image
    """
    # Convert to grayscale
    if img.mode != 'L':
        img = img.convert('L')
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)  # Increase contrast
    
    # Apply adaptive thresholding
    img_array = np.array(img)
    
    # Calculate adaptive threshold
    from scipy.ndimage import gaussian_filter
    blur_radius = 20
    blurred = gaussian_filter(img_array, sigma=blur_radius)
    threshold = blurred - 10  # Offset
    
    # Apply threshold
    binary = np.where(img_array > threshold, 255, 0).astype(np.uint8)
    img = Image.fromarray(binary)
    
    # Reduce noise with a median filter
    img = img.filter(ImageFilter.MedianFilter(size=3))
    
    # Sharpen edges
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    
    return img
# import io
# import tempfile
# from PIL import Image
# import streamlit as st

# def create_temp_file(text_file):
#     """
#     Creates a temporary file from an uploaded file and returns the path.
    
#     Args:
#         text_file: The file uploaded through Streamlit
        
#     Returns:
#         str: Path to the temporary file
#     """
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
#         temp_file.write(text_file.getbuffer())
#         return temp_file.name

# def get_image_bytes(image_file):
#     """
#     Converts an image file to bytes for API transmission.
    
#     Args:
#         image_file: The image file to convert
        
#     Returns:
#         bytes: The image converted to bytes
#     """
#     if image_file is None:
#         raise ValueError("❌ No image file was uploaded!")
        
#     # Open the image file
#     image = Image.open(image_file)
    
#     # Convert the image to bytes
#     image_bytes = io.BytesIO()
#     image.save(image_bytes, format=image.format or "JPEG")
    
#     return image_bytes.getvalue()