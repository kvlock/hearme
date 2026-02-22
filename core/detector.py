import cv2
import numpy as np
import tensorflow as tf
from utils.hand_detector import HandDetector
import os

class SignLanguageDetector:
    def __init__(self, model_path="./models/sign_language_model.tflite",
                 class_names_path="./models/class_names.npy"):
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        if not os.path.exists(class_names_path):
            raise FileNotFoundError(f"Class names file not found: {class_names_path}")
        
        print(f"Loading TFLite model from: {model_path}")
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        print(f"Model input shape: {self.input_details[0]['shape']}")
        print(f"Model output shape: {self.output_details[0]['shape']}")
        
        self.class_names = np.load(class_names_path, allow_pickle=True)
        print(f"Loaded {len(self.class_names)} classes: {self.class_names}")
        
        self.hand_detector = HandDetector(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
        
        self.current_phrase = ""
        self.last_prediction = None
        self.last_prediction_time = 0
        
        self.confidence_threshold = 0.6  
        self.stabilization_frames = 5    
        self.prediction_history = []
        
        self.debug_mode = True
    
    def process_frame(self, frame):
        
        frame_with_hands = self.hand_detector.find_hands(frame.copy(), draw=True)
        landmarks = self.hand_detector.get_landmarks(frame)
        
        prediction = None
        confidence = 0.0
        
        if landmarks and len(landmarks) > 0:
            
            landmarks_flat = np.array(landmarks).flatten().astype(np.float32)
            
            if self.debug_mode and len(self.prediction_history) % 30 == 0:
                print(f"Raw landmarks shape: {landmarks_flat.shape}")
                print(f"Landmarks range: [{landmarks_flat.min():.2f}, {landmarks_flat.max():.2f}]")
            
            landmarks_flat = landmarks_flat / 640.0
            
            input_shape = self.input_details[0]['shape']
            input_data = np.expand_dims(landmarks_flat, axis=0)
            
            if input_data.shape[1] != input_shape[1]:
                print(f"Warning: Input shape mismatch. Expected {input_shape[1]}, got {input_data.shape[1]}")
                
                if input_data.shape[1] > input_shape[1]:
                    input_data = input_data[:, :input_shape[1]]
                else:
                    padding = np.zeros((1, input_shape[1] - input_data.shape[1]))
                    input_data = np.concatenate([input_data, padding], axis=1)
            
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            self.interpreter.invoke()
            
            predictions = self.interpreter.get_tensor(self.output_details[0]['index'])
            confidence = np.max(predictions[0])
            predicted_idx = np.argmax(predictions[0])
            
            if confidence > self.confidence_threshold:
                prediction = self.class_names[predicted_idx]
                
                self.prediction_history.append(prediction)
                if len(self.prediction_history) > self.stabilization_frames:
                    self.prediction_history.pop(0)
                
                if len(self.prediction_history) == self.stabilization_frames:
                    if len(set(self.prediction_history)) == 1:  
                        stabilized_prediction = self.prediction_history[0]
                        
                        if stabilized_prediction != self.last_prediction:
                            self.last_prediction = stabilized_prediction
                            return frame_with_hands, landmarks, stabilized_prediction, confidence
                    else:
                        
                        return frame_with_hands, landmarks, None, confidence
        
        if not landmarks:
            self.prediction_history = []
            self.last_prediction = None
        
        return frame_with_hands, landmarks, prediction, confidence
    
    def get_hand_crop(self, frame, landmarks):
        
        if not landmarks:
            return None
        
        x_coords = [lm[0] for lm in landmarks]
        y_coords = [lm[1] for lm in landmarks]
        
        padding = 20
        x_min = max(0, min(x_coords) - padding)
        x_max = min(frame.shape[1], max(x_coords) + padding)
        y_min = max(0, min(y_coords) - padding)
        y_max = min(frame.shape[0], max(y_coords) + padding)
        
        hand_crop = frame[y_min:y_max, x_min:x_max]
        
        return hand_crop, (x_min, y_min, x_max, y_max)
    
    def add_to_phrase(self, letter):
        
        if letter and letter != self.last_prediction:
            self.current_phrase += letter
            self.last_prediction = letter
            return True
        return False
    
    def add_space(self):
        
        self.current_phrase += " "
        return True
    
    def clear_phrase(self):
        
        self.current_phrase = ""
        self.last_prediction = None
        self.prediction_history = []
        return True
    
    def get_phrase(self):
        
        return self.current_phrase
    
    def set_confidence_threshold(self, threshold):
        
        self.confidence_threshold = max(0.0, min(1.0, threshold))
    
    def set_debug_mode(self, enabled):
        
        self.debug_mode = enabled