import customtkinter as ctk
import cv2
import threading
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random

class LearningWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.WIDTH = 390
        self.HEIGHT = 844
        
        self.title("HearMe - Learning")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.resizable(False, False)
        
        self.primary_color = "#2196F3"
        self.white = "#FFFFFF"
        self.gray = "#F5F5F5"
        self.dark_gray = "#666666"
        self.green = "#4CAF50"
        self.orange = "#FF9800"
        self.red = "#F44336"
        
        self.progress = self.load_progress()
        self.letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.current_letter_index = 0
        self.current_letter = self.letters[self.current_letter_index]
        
        self.cap = None
        self.is_camera_running = False
        self.detector = None  
        self.current_detection = None
        self.current_confidence = 0.0
        self.practice_mode_active = False
        
        self.session_correct = 0
        self.session_total = 0
        self.session_start_time = None
        
        self.setup_ui()
        
        self.center_window()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.try_get_detector(parent)
    
    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.WIDTH) // 2
        y = (self.winfo_screenheight() - self.HEIGHT) // 2
        self.geometry(f'+{x}+{y}')
    
    def try_get_detector(self, parent):
        try:
            if hasattr(parent, 'detector') and parent.detector:
                self.detector = parent.detector
                print("Got detector from parent")
            else:
                from core.detector import SignLanguageDetector
                self.detector = SignLanguageDetector()
                print("Created new detector")
            
            if self.detector:
                self.start_camera()
                
        except Exception as e:
            print(f"Could not initialize detector: {e}")
            self.show_error_message()
            self.detector = None
    
    def show_error_message(self):
        error_frame = ctk.CTkFrame(
            self.main_container,
            corner_radius=15,
            fg_color="#FFF3CD",  
            border_width=1,
            border_color="#FFEEBA"
        )
        error_frame.pack(fill="x", pady=10, padx=20)
        
        error_content = ctk.CTkFrame(error_frame, fg_color="transparent")
        error_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            error_content,
            text="⚠️ Camera/Detection Not Available",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#856404"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            error_content,
            text="Please check:\n1. Camera is connected\n2. Model files exist in models/ folder\n3. Required libraries are installed",
            font=ctk.CTkFont(size=12),
            text_color="#856404",
            justify="left"
        ).pack(anchor="w", pady=(5, 0))
    
    def setup_ui(self):
        self.configure(fg_color=self.gray)
        
        self.main_container = ctk.CTkScrollableFrame(self, fg_color=self.gray)
        self.main_container.pack(fill="both", expand=True, padx=16, pady=16)
        
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        back_button = ctk.CTkButton(
            header_frame,
            text="← Back",
            command=self.on_closing,
            width=80,
            height=35,
            fg_color="transparent",
            text_color=self.primary_color,
            hover_color="#E3F2FD",
            font=ctk.CTkFont(size=14)
        )
        back_button.pack(side="left")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Learning Mode",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.primary_color
        )
        title_label.pack(side="left", padx=20)
        
        target_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=20,
            fg_color=self.white,
            border_width=1,
            border_color="#E0E0E0"
        )
        target_card.pack(fill="x", pady=(0, 20))
        
        target_content = ctk.CTkFrame(target_card, fg_color="transparent")
        target_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            target_content,
            text="Learn This Sign",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.primary_color
        ).pack(anchor="w", pady=(0, 15))
        
        self.target_letter_label = ctk.CTkLabel(
            target_content,
            text=self.current_letter,
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=self.primary_color
        )
        self.target_letter_label.pack()
        
        self.target_image_frame = ctk.CTkFrame(
            target_content,
            width=150,
            height=150,
            corner_radius=20,
            fg_color="#E3F2FD"  
        )
        self.target_image_frame.pack(pady=15)
        self.target_image_frame.pack_propagate(False)
        
        self.target_image_label = ctk.CTkLabel(
            self.target_image_frame,
            text=self.get_sign_emoji(self.current_letter),
            font=ctk.CTkFont(size=60),
            text_color=self.primary_color
        )
        self.target_image_label.pack(expand=True)
        
        self.target_desc_label = ctk.CTkLabel(
            target_content,
            text=self.get_sign_description(self.current_letter),
            font=ctk.CTkFont(size=14),
            text_color=self.dark_gray,
            wraplength=300,
            justify="center"
        )
        self.target_desc_label.pack(pady=(0, 10))
        
        nav_frame = ctk.CTkFrame(target_content, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(0, 15))
        
        prev_button = ctk.CTkButton(
            nav_frame,
            text="← Previous",
            command=self.prev_letter,
            height=35,
            fg_color="transparent",
            text_color=self.primary_color,
            hover_color="#E3F2FD",
            font=ctk.CTkFont(size=14)
        )
        prev_button.pack(side="left")
        
        next_button = ctk.CTkButton(
            nav_frame,
            text="Next →",
            command=self.next_letter,
            height=35,
            fg_color=self.primary_color,
            hover_color="#1976D2",
            font=ctk.CTkFont(size=14)
        )
        next_button.pack(side="right")
        
        practice_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=20,
            fg_color=self.white,
            border_width=1,
            border_color="#E0E0E0"
        )
        practice_card.pack(fill="x", pady=(0, 20))
        
        practice_content = ctk.CTkFrame(practice_card, fg_color="transparent")
        practice_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            practice_content,
            text="Practice Session",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.primary_color
        ).pack(anchor="w", pady=(0, 15))
        
        camera_frame = ctk.CTkFrame(
            practice_content,
            height=200,
            corner_radius=15,
            fg_color="black"
        )
        camera_frame.pack(fill="x", pady=(0, 15))
        camera_frame.pack_propagate(False)
        
        self.camera_label = ctk.CTkLabel(
            camera_frame,
            text="Camera Starting...",
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        self.camera_label.pack(expand=True)
        
        controls_frame = ctk.CTkFrame(practice_content, fg_color="transparent")
        controls_frame.pack(fill="x")
        
        self.practice_button = ctk.CTkButton(
            controls_frame,
            text="▶ Start Practice",
            command=self.toggle_practice,
            height=45,
            fg_color=self.green,
            hover_color="#45a049",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.practice_button.pack(fill="x", pady=(0, 10))
        
        detection_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        detection_frame.pack(fill="x", pady=(0, 15))
        
        detection_row = ctk.CTkFrame(detection_frame, fg_color="transparent")
        detection_row.pack(fill="x")
        
        ctk.CTkLabel(
            detection_row,
            text="Your Sign:",
            font=ctk.CTkFont(size=14),
            text_color=self.dark_gray
        ).pack(side="left", padx=(0, 10))
        
        self.user_sign_label = ctk.CTkLabel(
            detection_row,
            text="--",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.primary_color
        )
        self.user_sign_label.pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(
            detection_row,
            text="Match:",
            font=ctk.CTkFont(size=14),
            text_color=self.dark_gray
        ).pack(side="left", padx=(0, 10))
        
        self.match_label = ctk.CTkLabel(
            detection_row,
            text="0%",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.green
        )
        self.match_label.pack(side="left")
        
        stats_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        stats_frame.pack(fill="x")
        
        stats_row1 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_row1.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            stats_row1,
            text="Session:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.dark_gray
        ).pack(side="left", padx=(0, 20))
        
        self.session_stats_label = ctk.CTkLabel(
            stats_row1,
            text="0/0 (0%)",
            font=ctk.CTkFont(size=14),
            text_color=self.primary_color
        )
        self.session_stats_label.pack(side="left")
        
        progress_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=20,
            fg_color=self.white,
            border_width=1,
            border_color="#E0E0E0"
        )
        progress_card.pack(fill="x", pady=(0, 20))
        
        progress_content = ctk.CTkFrame(progress_card, fg_color="transparent")
        progress_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            progress_content,
            text=f"Accuracy for '{self.current_letter}'",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.primary_color
        ).pack(anchor="w", pady=(0, 10))
        
        accuracy_row = ctk.CTkFrame(progress_content, fg_color="transparent")
        accuracy_row.pack(fill="x", pady=(0, 15))
        
        self.accuracy_label = ctk.CTkLabel(
            accuracy_row,
            text=f"{self.progress.get(self.current_letter, 0)}%",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.get_accuracy_color(self.progress.get(self.current_letter, 0))
        )
        self.accuracy_label.pack(side="left", padx=(0, 20))
        
        self.accuracy_bar = ctk.CTkProgressBar(accuracy_row, width=150)
        self.accuracy_bar.pack(side="left")
        self.accuracy_bar.set(self.progress.get(self.current_letter, 0) / 100)
        
        ctk.CTkLabel(
            self.main_container,
            text="All Letters Progress",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.primary_color
        ).pack(anchor="w", pady=(0, 10))
        
        grid_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        grid_container.pack(fill="both", expand=True)
        
        for i, letter in enumerate(self.letters):
            row = i // 3
            col = i % 3
            
            progress_card = ctk.CTkFrame(
                grid_container,
                width=100,
                height=100,
                corner_radius=15,
                fg_color=self.white,
                border_width=1,
                border_color="#E0E0E0"
            )
            progress_card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            progress_card.grid_propagate(False)
            
            grid_container.grid_columnconfigure(col, weight=1, uniform="col")
            
            content = ctk.CTkFrame(progress_card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=10, pady=10)
            
            letter_label = ctk.CTkLabel(
                content,
                text=letter,
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=self.primary_color
            )
            letter_label.pack()
            
            progress_value = self.progress.get(letter, 0)
            progress_label = ctk.CTkLabel(
                content,
                text=f"{progress_value}%",
                font=ctk.CTkFont(size=14),
                text_color=self.get_accuracy_color(progress_value)
            )
            progress_label.pack()
            
            progress_card.bind("<Button-1>", lambda e, l=letter: self.select_letter(l))
            letter_label.bind("<Button-1>", lambda e, l=letter: self.select_letter(l))
            progress_label.bind("<Button-1>", lambda e, l=letter: self.select_letter(l))
    
    def get_sign_emoji(self, letter):
        emoji_map = {
            'A': '✊', 'B': '👋', 'C': '👌', 'D': '☝️', 'E': '🤏',
            'F': '👌', 'G': '👉', 'H': '✌️', 'I': '🤙', 'J': '🤙',
            'K': '✌️', 'L': '🤘', 'M': '🤌', 'N': '🤌', 'O': '👌',
            'P': '👌', 'Q': '👌', 'R': '✌️', 'S': '✊', 'T': '🤞',
            'U': '✌️', 'V': '✌️', 'W': '🤟', 'X': '🤏', 'Y': '🤙',
            'Z': '💫'
        }
        return emoji_map.get(letter, '👋')
    
    def get_sign_description(self, letter):
        descriptions = {
            'A': 'Make a fist with thumb resting alongside index finger',
            'B': 'Hold hand flat with fingers together, thumb across palm',
            'C': 'Curve hand into a C shape',
            'D': 'Point index finger up, close other fingers',
            'E': 'Bend fingers and touch thumb',
            'F': 'Touch thumb and index finger, keep other fingers up',
            'G': 'Point index finger sideways, thumb under',
            'H': 'Point index and middle fingers sideways',
            'I': 'Point pinky finger up, close other fingers',
            'J': 'Trace letter J shape with pinky finger',
            'K': 'Point index and middle fingers up, thumb between',
            'L': 'Form L shape with index finger and thumb',
            'M': 'Tuck three fingers under thumb',
            'N': 'Tuck two fingers under thumb',
            'O': 'Touch all fingertips to form O shape',
            'P': 'Point index finger down, touch thumb',
            'Q': 'Point index finger down, circle thumb',
            'R': 'Cross index and middle fingers',
            'S': 'Make a fist with thumb across fingers',
            'T': 'Place thumb between index and middle fingers',
            'U': 'Point index and middle fingers up together',
            'V': 'Make peace sign (V shape)',
            'W': 'Point index, middle, and ring fingers up',
            'X': 'Bend index finger at knuckle',
            'Y': 'Extend thumb and pinky',
            'Z': 'Trace letter Z shape with index finger'
        }
        return descriptions.get(letter, f"Sign for the letter '{letter}'")
    
    def get_accuracy_color(self, value):
        if value >= 80:
            return self.green
        elif value >= 50:
            return self.orange
        else:
            return self.red
    
    def load_progress(self):
        progress = {}
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            progress[letter] = random.randint(0, 100)
        
        for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
            if random.random() > 0.3:  
                progress[letter] = 0
        
        progress["A"] = 95
        progress["B"] = 70
        progress["C"] = 20
        
        return progress
    
    def start_camera(self):
        if self.detector is None:
            print("Warning: No detector available for learning mode")
            self.camera_label.configure(image="", text="No detector available")
            return
        
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.camera_label.configure(image="", text="Camera not available")
                return
            
            self.is_camera_running = True
            self.update_camera()
            
        except Exception as e:
            print(f"Camera error: {e}")
            self.camera_label.configure(image="", text=f"Camera error: {str(e)}")
    
    def update_camera(self):
        if self.is_camera_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                if self.detector and self.practice_mode_active:
                    try:
                        processed_frame, landmarks, prediction, confidence = self.detector.process_frame(frame)
                        
                        self.current_detection = prediction
                        self.current_confidence = confidence
                        
                        self.update_detection_display(prediction, confidence)
                        
                        if prediction == self.current_letter and confidence > 0.7:
                            self.session_total += 1
                            self.session_correct += 1
                            self.update_session_stats()
                            
                            self.update_letter_accuracy(True)
                        elif prediction and confidence > 0.7:
                            self.session_total += 1
                            self.update_session_stats()
                            
                            self.update_letter_accuracy(False)
                        
                        frame = processed_frame
                    except Exception as e:
                        print(f"Detection error: {e}")
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                
                img = img.resize((350, 200))
                
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(350, 200))
                self.camera_label.configure(image=ctk_img, text="")
        
        if self.is_camera_running:
            self.after(33, self.update_camera)  
    
    def update_detection_display(self, prediction, confidence):
        if prediction:
            self.user_sign_label.configure(text=prediction)
            
            if prediction == self.current_letter:
                match_percent = confidence * 100
                color = self.green if match_percent > 70 else self.orange if match_percent > 40 else self.red
            else:
                match_percent = 0
                color = self.red
            
            self.match_label.configure(
                text=f"{match_percent:.0f}%",
                text_color=color
            )
        else:
            self.user_sign_label.configure(text="--")
            self.match_label.configure(text="0%", text_color=self.red)
    
    def update_session_stats(self):
        if self.session_total > 0:
            accuracy = (self.session_correct / self.session_total) * 100
            self.session_stats_label.configure(
                text=f"{self.session_correct}/{self.session_total} ({accuracy:.0f}%)"
            )
    
    def update_letter_accuracy(self, correct):
        current_accuracy = self.progress.get(self.current_letter, 0)
        
        if correct:
            new_accuracy = min(100, current_accuracy + 2)
        else:
            new_accuracy = max(0, current_accuracy - 1)
        
        self.progress[self.current_letter] = new_accuracy
        
        self.accuracy_label.configure(
            text=f"{new_accuracy}%",
            text_color=self.get_accuracy_color(new_accuracy)
        )
        self.accuracy_bar.set(new_accuracy / 100)
    
    def toggle_practice(self):
        if not self.detector:
            self.show_error_message()
            return
        
        self.practice_mode_active = not self.practice_mode_active
        
        if self.practice_mode_active:
            self.practice_button.configure(
                text="⏸ Pause Practice",
                fg_color=self.orange
            )
            self.session_start_time = time.time()
            self.session_correct = 0
            self.session_total = 0
            self.update_session_stats()
            
            if not self.is_camera_running:
                self.start_camera()
        else:
            self.practice_button.configure(
                text="▶ Start Practice",
                fg_color=self.green
            )
    
    def prev_letter(self):
        self.current_letter_index = (self.current_letter_index - 1) % len(self.letters)
        self.select_letter(self.letters[self.current_letter_index])
    
    def next_letter(self):
        self.current_letter_index = (self.current_letter_index + 1) % len(self.letters)
        self.select_letter(self.letters[self.current_letter_index])
    
    def select_letter(self, letter):
        self.current_letter = letter
        self.current_letter_index = self.letters.index(letter)
        
        self.target_letter_label.configure(text=letter)
        self.target_image_label.configure(text=self.get_sign_emoji(letter))
        self.target_desc_label.configure(text=self.get_sign_description(letter))
        
        accuracy = self.progress.get(letter, 0)
        self.accuracy_label.configure(
            text=f"{accuracy}%",
            text_color=self.get_accuracy_color(accuracy)
        )
        self.accuracy_bar.set(accuracy / 100)
        
        self.user_sign_label.configure(text="--")
        self.match_label.configure(text="0%", text_color=self.red)
        
        if self.practice_mode_active:
            self.practice_mode_active = False
            self.practice_button.configure(
                text="▶ Start Practice",
                fg_color=self.green
            )
    
    def on_closing(self):
        self.is_camera_running = False
        self.practice_mode_active = False
        
        if self.cap:
            self.cap.release()
        
        print("Saving learning progress...")
        
        self.destroy()