import customtkinter as ctk
import speech_recognition as sr
import threading

class SpeechWindow(ctk.CTkToplevel):
    def __init__(self, parent, tts):
        super().__init__(parent)
        
        self.WIDTH = 390
        self.HEIGHT = 844
        
        self.title("HearMe - Speech")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.resizable(False, False)
        
        self.tts = tts
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        
        self.primary_color = "#2196F3"
        self.white = "#FFFFFF"
        self.gray = "#F5F5F5"
        self.dark_gray = "#666666"
        self.green = "#4CAF50"
        
        self.setup_ui()
        self.center_window()
    
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
            command=self.destroy,
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
            text="Speech Conversion",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.primary_color
        )
        title_label.pack(side="left", padx=20)
        
        mode_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=20,
            fg_color=self.white,
            border_width=1,
            border_color="#E0E0E0"
        )
        mode_card.pack(fill="x", pady=(0, 20))
        
        mode_content = ctk.CTkFrame(mode_card, fg_color="transparent")
        mode_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            mode_content,
            text="Select Mode",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.primary_color
        ).pack(anchor="w", pady=(0, 15))
        
        self.mode_var = ctk.StringVar(value="speech_to_text")
        
        mode_frame = ctk.CTkFrame(mode_content, fg_color="transparent")
        mode_frame.pack(fill="x")
        
        speech_to_text_btn = ctk.CTkButton(
            mode_frame,
            text="🎤 Speech to Text",
            command=lambda: self.set_mode("speech_to_text"),
            height=45,
            fg_color=self.primary_color if self.mode_var.get() == "speech_to_text" else "#E0E0E0",
            text_color="white" if self.mode_var.get() == "speech_to_text" else "#666666",
            hover_color="#1976D2" if self.mode_var.get() == "speech_to_text" else "#D0D0D0",
            font=ctk.CTkFont(size=15)
        )
        speech_to_text_btn.pack(side="left", expand=True, padx=(0, 5))
        
        text_to_speech_btn = ctk.CTkButton(
            mode_frame,
            text="🔊 Text to Speech",
            command=lambda: self.set_mode("text_to_speech"),
            height=45,
            fg_color=self.primary_color if self.mode_var.get() == "text_to_speech" else "#E0E0E0",
            text_color="white" if self.mode_var.get() == "text_to_speech" else "#666666",
            hover_color="#1976D2" if self.mode_var.get() == "text_to_speech" else "#D0D0D0",
            font=ctk.CTkFont(size=15)
        )
        text_to_speech_btn.pack(side="left", expand=True, padx=(5, 0))
        
        display_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=20,
            fg_color=self.white,
            border_width=1,
            border_color="#E0E0E0"
        )
        display_card.pack(fill="x", pady=(0, 20))
        
        display_content = ctk.CTkFrame(display_card, fg_color="transparent")
        display_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            display_content,
            text="Text",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.primary_color
        ).pack(anchor="w", pady=(0, 10))
        
        self.text_display = ctk.CTkTextbox(
            display_content,
            height=120,
            font=ctk.CTkFont(size=16),
            border_width=1,
            border_color="#E0E0E0",
            fg_color="#FAFAFA"
        )
        self.text_display.pack(fill="x", pady=(0, 15))
        self.text_display.insert("1.0", "Hello World")
        
        self.input_frame = ctk.CTkFrame(
            self.main_container,
            corner_radius=20,
            fg_color=self.white,
            border_width=1,
            border_color="#E0E0E0"
        )
        self.input_frame.pack(fill="x", pady=(0, 20))
        
        input_content = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        input_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            input_content,
            text="Enter Text",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.primary_color
        ).pack(anchor="w", pady=(0, 10))
        
        self.text_input = ctk.CTkEntry(
            input_content,
            placeholder_text="Type text to convert to speech...",
            height=45,
            font=ctk.CTkFont(size=16),
            border_width=1,
            border_color="#E0E0E0"
        )
        self.text_input.pack(fill="x")
        
        action_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        action_frame.pack(fill="x")
        
        self.listen_button = ctk.CTkButton(
            action_frame,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            height=50,
            fg_color=self.green,
            hover_color="#45a049",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.listen_button.pack(fill="x", pady=(0, 10))
        
        self.speak_button = ctk.CTkButton(
            action_frame,
            text="🔊 Speak Text",
            command=self.speak_text,
            height=50,
            fg_color=self.primary_color,
            hover_color="#1976D2",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.speak_button.pack(fill="x")
        
        self.update_mode_ui()
    
    def set_mode(self, mode):
        self.mode_var.set(mode)
        self.update_mode_ui()
        
        for widget in self.main_container.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkFrame):
                        for btn in child.winfo_children():
                            if isinstance(btn, ctk.CTkButton):
                                if "Speech to Text" in btn.cget("text"):
                                    if mode == "speech_to_text":
                                        btn.configure(fg_color=self.primary_color, text_color="white")
                                    else:
                                        btn.configure(fg_color="#E0E0E0", text_color="#666666")
                                elif "Text to Speech" in btn.cget("text"):
                                    if mode == "text_to_speech":
                                        btn.configure(fg_color=self.primary_color, text_color="white")
                                    else:
                                        btn.configure(fg_color="#E0E0E0", text_color="#666666")
    
    def update_mode_ui(self):
        mode = self.mode_var.get()
        
        if mode == "speech_to_text":
            self.listen_button.configure(state="normal")
            self.speak_button.configure(state="disabled")
            self.input_frame.pack_forget()
        else:
            self.listen_button.configure(state="disabled")
            self.speak_button.configure(state="normal")
            self.input_frame.pack(fill="x", pady=(0, 20))
    
    def toggle_listening(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        self.is_listening = True
        self.listen_button.configure(text="⏸️ Stop Listening", fg_color=self.primary_color)
        threading.Thread(target=self.recognize_speech, daemon=True).start()
    
    def stop_listening(self):
        self.is_listening = False
        self.listen_button.configure(text="🎤 Start Listening", fg_color=self.green)
    
    def recognize_speech(self):
        try:
            with sr.Microphone() as source:
                self.after(0, self.update_status, "Listening... Speak now")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                while self.is_listening:
                    try:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        
                        self.after(0, self.update_status, "Recognizing...")
                        text = self.recognizer.recognize_google(audio)
                        
                        self.after(0, self.update_display, text)
                        self.after(0, self.update_status, "Ready")
                        
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        self.after(0, self.update_status, "Could not understand audio")
                    except sr.RequestError as e:
                        self.after(0, self.update_status, f"Recognition error: {e}")
        
        except Exception as e:
            self.after(0, self.update_status, f"Error: {str(e)}")
        
        self.is_listening = False
        self.after(0, lambda: self.listen_button.configure(
            text="🎤 Start Listening", fg_color=self.green
        ))
    
    def speak_text(self):
        if self.mode_var.get() == "text_to_speech":
            text = self.text_input.get()
        else:
            text = self.text_display.get("1.0", "end-1c")
        
        if text:
            self.tts.speak(text)
    
    def update_display(self, text):
        self.text_display.delete("1.0", "end")
        self.text_display.insert("1.0", text)
    
    def update_status(self, message):
        print(f"Speech Recognition: {message}")