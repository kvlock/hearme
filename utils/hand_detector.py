import cv2
import mediapipe as mp
import numpy as np

class HandDetector:
    def __init__(self, static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5):
        """
        Initialize MediaPipe hand detector
        
        Args:
            static_image_mode: If True, treats input images as static
            max_num_hands: Maximum number of hands to detect
            min_detection_confidence: Minimum confidence for hand detection
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None
        
        # Custom drawing specs
        self.landmark_drawing_spec = self.mp_draw.DrawingSpec(
            color=(0, 255, 0),  
            thickness=2,
            circle_radius=3
        )
        
        self.connection_drawing_spec = self.mp_draw.DrawingSpec(
            color=(255, 0, 0),  
            thickness=2
        )
    
    def find_hands(self, img, draw=True):
        """
        Find hands in image
        
        Args:
            img: Input image (BGR format)
            draw: If True, draw landmarks on image
            
        Returns:
            Image with landmarks drawn (if draw=True)
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        self.results = self.hands.process(img_rgb)
        
        if draw and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.landmark_drawing_spec,
                    self.connection_drawing_spec
                )
        
        return img
    
    def get_landmarks(self, img, hand_number=0):
        """
        Get hand landmarks
        
        Args:
            img: Input image (for dimensions)
            hand_number: Which hand to get landmarks from (0-indexed)
            
        Returns:
            List of [x, y] coordinates for each landmark, or empty list if no hand
        """
        landmarks = []
        
        if self.results and self.results.multi_hand_landmarks:
            if hand_number < len(self.results.multi_hand_landmarks):
                hand = self.results.multi_hand_landmarks[hand_number]
                h, w, _ = img.shape
                
                for landmark in hand.landmark:
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    landmarks.append([cx, cy])
        
        return landmarks
    
    def get_all_landmarks(self, img):
        """
        Get landmarks for all detected hands
        
        Returns:
            List of lists, where each inner list contains landmarks for one hand
        """
        all_landmarks = []
        
        if self.results and self.results.multi_hand_landmarks:
            h, w, _ = img.shape
            
            for hand in self.results.multi_hand_landmarks:
                hand_landmarks = []
                for landmark in hand.landmark:
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    hand_landmarks.append([cx, cy])
                all_landmarks.append(hand_landmarks)
        
        return all_landmarks
    
    def get_handedness(self):
        """
        Get handedness (left/right) for detected hands
        
        Returns:
            List of strings ("Left" or "Right") for each detected hand
        """
        handedness = []
        
        if self.results and self.results.multi_handedness:
            for hand_info in self.results.multi_handedness:
                label = hand_info.classification[0].label
                handedness.append(label)
        
        return handedness
    
    def get_bounding_box(self, img, hand_number=0):
        """
        Get bounding box for a hand
        
        Returns:
            (x_min, y_min, x_max, y_max) or None if no hand
        """
        landmarks = self.get_landmarks(img, hand_number)
        
        if not landmarks:
            return None
        
        x_coords = [lm[0] for lm in landmarks]
        y_coords = [lm[1] for lm in landmarks]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        padding = 20
        h, w, _ = img.shape
        
        x_min = max(0, x_min - padding)
        x_max = min(w, x_max + padding)
        y_min = max(0, y_min - padding)
        y_max = min(h, y_max + padding)
        
        return (x_min, y_min, x_max, y_max)
    
    def draw_bounding_box(self, img, bbox, color=(0, 255, 0), thickness=2):
        """Draw bounding box on image"""
        if bbox:
            x_min, y_min, x_max, y_max = bbox
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), color, thickness)
        return img
    
    def release(self):
        """Release resources"""
        if self.hands:
            self.hands.close()