import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import threading
import numpy as np
import time

class DetectionWindow(ctk.CTkToplevel):
    def __init__(self, parent, detector, tts):
        super().__init__(parent)
        
        self.WIDTH = 390
        self.HEIGHT = 844
        
        self.title("HearMe - Detection")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.resizable(False, False)
        
        self.detector = detector
        self.tts = tts
        self.is_running = True
        
        self.primary_color = "#2196F3"
        self.white = "#FFFFFF"
        self.gray = "#F5F5F5"
        self.dark_gray = "#666666"
        self.green = "#4CAF50"
        
        self.last_tts_time = 0
        self.tts_cooldown = 1.0
        self.current_phrase = ""
        
        self.setup_ui()
        
        self.start_camera()
        
        self.center_window()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.WIDTH) // 2
        y = (self.winfo_screenheight() - self.HEIGHT) // 2
        self.geometry(f'+{x}+{y}')
    
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
            text="Gesture Detection",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.primary_color
        )
        title_label.pack(side="left", padx=20)
        
        camera_frame = ctk.CTkFrame(
            self.main_container,
            height=300,
            corner_radius=20,
            fg_color="black"
        )
        camera_frame.pack(fill="x", pady=(0, 20))
        camera_frame.pack_propagate(False)
        
        self.camera_label = ctk.CTkLabel(
            camera_frame,
            text="Starting camera...",
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        self.camera_label.pack(expand=True)
        
        info_card = ctk.CTkFrame(
            self.main_container,
            height=120,
            corner_radius=20,
            fg_color=self.white,
            border_width=1,
            border_color="#E0E0E0"
        )
        info_card.pack(fill="x", pady=(0, 20))
        info_card.pack_propagate(False)
        
        info_content = ctk.CTkFrame(info_card, fg_color="transparent")
        info_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        ctk.CTkLabel(
            info_content,
            text="Current Detection",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.dark_gray
        ).pack(anchor="w")
        
        detection_row = ctk.CTkFrame(info_content, fg_color="transparent")
        detection_row.pack(fill="x", pady=(5, 0))
        
        self.detected_letter_label = ctk.CTkLabel(
            detection_row,
            text="--",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=self.primary_color
        )
        self.detected_letter_label.pack(side="left", padx=(0, 20))
        
        confidence_frame = ctk.CTkFrame(detection_row, fg_color="transparent")
        confidence_frame.pack(side="left", fill="y")
        
        ctk.CTkLabel(
            confidence_frame,
            text="Confidence",
            font=ctk.CTkFont(size=12),
            text_color=self.dark_gray
        ).pack(anchor="w")
        
        self.confidence_label = ctk.CTkLabel(
            confidence_frame,
            text="0%",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.green
        )
        self.confidence_label.pack(anchor="w", pady=(2, 0))
        
        phrase_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=20,
            fg_color=self.white,
            border_width=1,
            border_color="#E0E0E0"
        )
        phrase_card.pack(fill="x", pady=(0, 20))
        
        phrase_content = ctk.CTkFrame(phrase_card, fg_color="transparent")
        phrase_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            phrase_content,
            text="Your Phrase",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.primary_color
        ).pack(anchor="w", pady=(0, 10))
        
        self.phrase_display = ctk.CTkTextbox(
            phrase_content,
            height=80,
            font=ctk.CTkFont(size=18, weight="bold"),
            border_width=1,
            border_color="#E0E0E0",
            fg_color="#FAFAFA"
        )
        self.phrase_display.pack(fill="x", pady=(0, 15))
        self.phrase_display.insert("1.0", "")
        
        actions_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        actions_frame.pack(fill="x")
        
        row1 = ctk.CTkFrame(actions_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        
        buttons_row1 = [
            ("Confirm", "#4CAF50", self.confirm_letter),
            ("Add Space", "#FF9800", self.add_space)
        ]
        
        for text, color, command in buttons_row1:
            btn = ctk.CTkButton(
                row1,
                text=text,
                command=command,
                height=45,
                fg_color=color,
                hover_color=self._darken_color(color),
                font=ctk.CTkFont(size=15)
            )
            btn.pack(side="left", expand=True, padx=5)
        
        row2 = ctk.CTkFrame(actions_frame, fg_color="transparent")
        row2.pack(fill="x")
        
        buttons_row2 = [
            ("Clear", "#F44336", self.clear_phrase),
            ("Speak", "#2196F3", self.speak_phrase)
        ]
        
        for text, color, command in buttons_row2:
            btn = ctk.CTkButton(
                row2,
                text=text,
                command=command,
                height=45,
                fg_color=color,
                hover_color=self._darken_color(color),
                font=ctk.CTkFont(size=15)
            )
            btn.pack(side="left", expand=True, padx=5)
    
    def _darken_color(self, hex_color):
        if hex_color == "#4CAF50":
            return "#45a049"
        elif hex_color == "#FF9800":
            return "#f57c00"
        elif hex_color == "#F44336":
            return "#d32f2f"
        elif hex_color == "#2196F3":
            return "#1976D2"
        return hex_color
    
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.camera_thread = threading.Thread(target=self.update_camera)
        self.camera_thread.daemon = True
        self.camera_thread.start()
    
    def update_camera(self):
        while self.is_running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                processed_frame, landmarks, prediction, confidence = self.detector.process_frame(frame)
                
                self.after(0, self.update_display, processed_frame, prediction, confidence)
            
            time.sleep(0.03)
        
        self.cap.release()
    
    def update_display(self, frame, prediction, confidence):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        
        img = img.resize((350, 250))
        
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(350, 250))
        self.camera_label.configure(image=ctk_img, text="")
        
        if prediction:
            self.detected_letter_label.configure(text=prediction)
            self.confidence_label.configure(text=f"{confidence:.1%}")
        else:
            self.detected_letter_label.configure(text="--")
            self.confidence_label.configure(text="0%")
    
    def confirm_letter(self):
        current_text = self.detected_letter_label.cget("text")
        
        if current_text != "--":
            self.current_phrase += current_text
            self.phrase_display.delete("1.0", "end")
            self.phrase_display.insert("1.0", self.current_phrase)
            
            current_time = time.time()
            if current_time - self.last_tts_time > self.tts_cooldown:
                self.tts.speak_letter(current_text)
                self.last_tts_time = current_time
    
    def add_space(self):
        self.current_phrase += " "
        self.phrase_display.delete("1.0", "end")
        self.phrase_display.insert("1.0", self.current_phrase)
    
    def clear_phrase(self):
        self.current_phrase = ""
        self.phrase_display.delete("1.0", "end")
    
    def speak_phrase(self):
        if self.current_phrase:
            self.tts.speak(self.current_phrase)
    
    def on_closing(self):
        self.is_running = False
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        self.destroy()