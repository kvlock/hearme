import os
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import customtkinter as ctk
import json
import pickle
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def create_ctk_image(image_path, size=None):
    """
    Create CTkImage from file path
    
    Args:
        image_path: Path to image file
        size: Optional tuple (width, height) to resize image
        
    Returns:
        CTkImage object or placeholder if image not found
    """
    try:
        if not os.path.exists(image_path):
            logger.warning(f"Image not found: {image_path}")
            return create_placeholder_image(size)
        
        image = Image.open(image_path)
        if size:
            image = image.resize(size)
        return ctk.CTkImage(light_image=image, dark_image=image)
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        return create_placeholder_image(size)

def create_placeholder_image(size=(100, 100), text="Image", color="#2196F3"):
    """
    Create a placeholder image with text
    
    Args:
        size: Image dimensions (width, height)
        text: Text to display on placeholder
        color: Background color
        
    Returns:
        CTkImage placeholder
    """
    if not size:
        size = (100, 100)
    
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    
    try:
        font_size = min(size) // 4
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    bg_color = Image.new('RGB', (1, 1), color)
    avg_color = np.array(bg_color).mean()
    text_color = "white" if avg_color < 128 else "black"
    
    draw.text(position, text, fill=text_color, font=font)
    
    return ctk.CTkImage(light_image=img, dark_image=img)

def get_letter_image(letter, size=(150, 150)):
    """
    Get image for a letter sign
    
    Args:
        letter: Single character A-Z
        size: Image dimensions
        
    Returns:
        CTkImage of the sign
    """
    image_path = f"assets/signs/{letter}.png"
    if os.path.exists(image_path):
        return create_ctk_image(image_path, size)
    
    return create_placeholder_image(size, letter, "#4CAF50")

def draw_landmarks_on_image(image, landmarks, connections=None, color=(0, 255, 0), thickness=2):
    """
    Draw hand landmarks and connections on image
    
    Args:
        image: OpenCV image (BGR format)
        landmarks: List of [x, y] coordinates
        connections: List of connection pairs (default: hand connections)
        color: BGR color tuple
        thickness: Line thickness
        
    Returns:
        Image with landmarks drawn
    """
    img_copy = image.copy()
    
    if not landmarks:
        return img_copy
    
    for idx, (x, y) in enumerate(landmarks):
        cv2.circle(img_copy, (x, y), thickness * 2, color, -1)

    if connections:
        for connection in connections:
            start_idx, end_idx = connection
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                start_point = landmarks[start_idx]
                end_point = landmarks[end_idx]
                cv2.line(img_copy, start_point, end_point, color, thickness)
    
    return img_copy

def draw_bounding_box(image, bbox, color=(0, 255, 0), thickness=2, label=None):
    """
    Draw bounding box on image
    
    Args:
        image: OpenCV image
        bbox: Tuple (x_min, y_min, x_max, y_max)
        color: BGR color tuple
        thickness: Line thickness
        label: Optional label text
        
    Returns:
        Image with bounding box
    """
    img_copy = image.copy()
    
    if not bbox:
        return img_copy
    
    x_min, y_min, x_max, y_max = bbox
    cv2.rectangle(img_copy, (x_min, y_min), (x_max, y_max), color, thickness)
    
    if label:
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        cv2.rectangle(img_copy, 
                     (x_min, y_min - text_size[1] - 10), 
                     (x_min + text_size[0] + 10, y_min), 
                     color, -1)
        cv2.putText(img_copy, label, (x_min + 5, y_min - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return img_copy

def crop_hand_region(image, bbox):
    """
    Crop hand region from image
    
    Args:
        image: OpenCV image
        bbox: Tuple (x_min, y_min, x_max, y_max)
        
    Returns:
        Cropped hand image or None
    """
    if not bbox:
        return None
    
    x_min, y_min, x_max, y_max = bbox
    
    h, w = image.shape[:2]
    x_min = max(0, x_min)
    y_min = max(0, y_min)
    x_max = min(w, x_max)
    y_max = min(h, y_max)
    
    if x_min >= x_max or y_min >= y_max:
        return None
    
    return image[y_min:y_max, x_min:x_max]

def create_progress_color(value):
    """
    Create color based on progress value (0-100)
    
    Args:
        value: Progress value (0-100)
        
    Returns:
        Hex color code
    """
    value = max(0, min(100, value))
    
    if value >= 80:
        return "#4CAF50"  
    elif value >= 60:
        return "#8BC34A"  
    elif value >= 40:
        return "#FFC107"  
    elif value >= 20:
        return "#FF9800" 
    else:
        return "#F44336"  

def format_confidence(confidence):
    """
    Format confidence as percentage string
    
    Args:
        confidence: Confidence value (0-1)
        
    Returns:
        Formatted string (e.g., "95.5%")
    """
    return f"{confidence * 100:.1f}%"

def format_time_duration(seconds):
    """
    Format time duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2m 30s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}m {seconds}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def validate_model_files(model_path, class_names_path):
    """
    Validate that required model files exist and are valid
    
    Args:
        model_path: Path to .tflite model file
        class_names_path: Path to class names file
        
    Returns:
        Tuple (is_valid, error_messages)
    """
    errors = []
    
    if not os.path.exists(model_path):
        errors.append(f"Model file not found: {model_path}")
    
    if not os.path.exists(class_names_path):
        errors.append(f"Class names file not found: {class_names_path}")
    
    if not errors:
        try:
            class_names = np.load(class_names_path, allow_pickle=True)
            if len(class_names) == 0:
                errors.append("Class names file is empty")
            elif len(class_names) != 26:
                logger.warning(f"Expected 26 classes (A-Z), got {len(class_names)}")
        except Exception as e:
            errors.append(f"Error loading class names: {e}")
        
        try:
            file_size = os.path.getsize(model_path)
            if file_size < 1024:  # Less than 1KB is suspicious
                errors.append(f"Model file seems too small: {file_size} bytes")
        except Exception as e:
            errors.append(f"Error checking model file: {e}")
    
    return len(errors) == 0, errors

def setup_directories():
    """
    Create necessary directories if they don't exist
    """
    directories = [
        "models",
        "assets",
        "assets/signs",
        "assets/icons",
        "logs",
        "exports",
        "data",
        "checkpoints"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

def save_settings(settings):
    """
    Save application settings to JSON file
    
    Args:
        settings: Dictionary of settings
    """
    try:
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=2)
        logger.info("Settings saved successfully")
    except Exception as e:
        logger.error(f"Error saving settings: {e}")

def load_settings(default_settings=None):
    """
    Load application settings from JSON file
    
    Args:
        default_settings: Default settings if file doesn't exist
        
    Returns:
        Dictionary of settings
    """
    if default_settings is None:
        default_settings = {
            "camera_index": 0,
            "confidence_threshold": 0.7,
            "stabilization_frames": 5,
            "tts_rate": 170,
            "tts_volume": 0.9,
            "theme": "light",
            "language": "en"
        }
    
    try:
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                loaded_settings = json.load(f)
            
            settings = {**default_settings, **loaded_settings}
            logger.info("Settings loaded successfully")
            return settings
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
    
    return default_settings

def save_learning_progress(progress):
    """
    Save learning progress
    
    Args:
        progress: Dictionary with letter -> accuracy mapping
    """
    try:
        progress_data = {
            "timestamp": datetime.now().isoformat(),
            "progress": progress
        }
        
        with open("data/learning_progress.pkl", "wb") as f:
            pickle.dump(progress_data, f)
        logger.info("Learning progress saved")
    except Exception as e:
        logger.error(f"Error saving learning progress: {e}")

def load_learning_progress():
    """
    Load learning progress
    
    Returns:
        Dictionary with letter -> accuracy mapping
    """
    try:
        if os.path.exists("data/learning_progress.pkl"):
            with open("data/learning_progress.pkl", "rb") as f:
                progress_data = pickle.load(f)
            logger.info("Learning progress loaded")
            return progress_data.get("progress", {})
    except Exception as e:
        logger.error(f"Error loading learning progress: {e}")
    
    return {letter: 0 for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}

def export_phrase_history(phrases, filename=None):
    """
    Export phrase history to text file
    
    Args:
        phrases: List of phrases
        filename: Output filename (optional)
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exports/phrases_{timestamp}.txt"
    
    try:
        os.makedirs("exports", exist_ok=True)
        
        with open(filename, "w") as f:
            f.write("HeartMe - Sign Language Phrases\n")
            f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            for i, phrase in enumerate(phrases, 1):
                f.write(f"{i:3d}. {phrase}\n")
        
        logger.info(f"Phrases exported to: {filename}")
        return True
    except Exception as e:
        logger.error(f"Error exporting phrases: {e}")
        return False

def create_gradient_image(width, height, start_color, end_color, horizontal=True):
    """
    Create a gradient image
    
    Args:
        width: Image width
        height: Image height
        start_color: Starting color (hex)
        end_color: Ending color (hex)
        horizontal: True for horizontal gradient, False for vertical
        
    Returns:
        PIL Image with gradient
    """
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)

    if horizontal:
        gradient = np.zeros((height, width, 3), dtype=np.uint8)
        for x in range(width):
            ratio = x / width
            color = [
                int(start_rgb[i] * (1 - ratio) + end_rgb[i] * ratio)
                for i in range(3)
            ]
            gradient[:, x] = color
    else:
        gradient = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            ratio = y / height
            color = [
                int(start_rgb[i] * (1 - ratio) + end_rgb[i] * ratio)
                for i in range(3)
            ]
            gradient[y, :] = color
    
    return Image.fromarray(gradient)

def center_window(window, width=None, height=None):
    """
    Center a tkinter window on screen
    
    Args:
        window: Tkinter or CTk window
        width: Window width (optional, uses current if None)
        height: Window height (optional, uses current if None)
    """
    if width is None or height is None:
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
    
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")

def validate_email(email):
    """
    Simple email validation
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_system_info():
    """
    Get system information
    
    Returns:
        Dictionary with system info
    """
    import platform
    
    info = {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "node": platform.node(),
    }
    
    return info

def create_tooltip(widget, text):
    """
    Create a tooltip for a widget
    
    Args:
        widget: The widget to attach tooltip to
        text: Tooltip text
    """

    widget.bind("<Enter>", lambda e: logger.info(f"Tooltip: {text}"))

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),  # Index finger
    (0, 9), (9, 10), (10, 11), (11, 12),  # Middle finger
    (0, 13), (13, 14), (14, 15), (15, 16),  # Ring finger
    (0, 17), (17, 18), (18, 19), (19, 20)  # Pinky
]

ASL_ALPHABET = {
    'A': 'Closed fist with thumb resting alongside',
    'B': 'Flat hand with fingers together, thumb across palm',
    'C': 'Curved hand shaped like letter C',
    'D': 'Index finger pointing up, other fingers closed',
    'E': 'Fingers bent and touching thumb',
    'F': 'Index finger and thumb forming circle, other fingers up',
    'G': 'Index finger pointing sideways, thumb under',
    'H': 'Index and middle fingers pointing sideways',
    'I': 'Pinky finger up, other fingers closed',
    'J': 'Pinky finger traces letter J shape',
    'K': 'Index and middle fingers up and apart, thumb between',
    'L': 'Index finger and thumb forming L shape',
    'M': 'Three fingers tucked under thumb',
    'N': 'Two fingers tucked under thumb',
    'O': 'All fingertips touching forming O shape',
    'P': 'Index finger and thumb forming P shape, hanging down',
    'Q': 'Index finger and thumb forming circle, hanging down',
    'R': 'Index and middle fingers crossed',
    'S': 'Closed fist with thumb across fingers',
    'T': 'Thumb between index and middle fingers',
    'U': 'Index and middle fingers up together',
    'V': 'Index and middle fingers up and apart (peace sign)',
    'W': 'Index, middle, and ring fingers up',
    'X': 'Index finger bent at knuckle',
    'Y': 'Thumb and pinky extended',
    'Z': 'Index finger traces letter Z shape'
}

if __name__ == "__main__":
    print("Testing helper functions...")
    
    setup_directories()
    
    print(f"Progress color for 95: {create_progress_color(95)}")
    print(f"Progress color for 50: {create_progress_color(50)}")
    print(f"Progress color for 10: {create_progress_color(10)}")
    
    print(f"Formatted confidence: {format_confidence(0.955)}")

    print(f"Formatted time (45s): {format_time_duration(45)}")
    print(f"Formatted time (125s): {format_time_duration(125)}")
    print(f"Formatted time (3725s): {format_time_duration(3725)}")
    
    print("Helper functions test complete!")