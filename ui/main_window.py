import customtkinter as ctk
from core.detector import SignLanguageDetector
from core.tts_manager import TTSManager
from ui.detection_window import DetectionWindow
from ui.library_window import LibraryWindow
from ui.learning_window import LearningWindow
from ui.speech_window import SpeechWindow

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.WIDTH = 390
        self.HEIGHT = 844
        
        self.title("HearMe")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.resizable(False, False) 
        
        self.primary_color = "#2196F3"  
        self.secondary_color = "#FFFFFF" 
        self.accent_color = "#4CAF50"  
        self.background_color = "#F5F5F5"  
        
        try:
            from core.detector import SignLanguageDetector
            print("Initializing detector...")
            self.detector = SignLanguageDetector()
            print("Detector initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize detector: {e}")
            self.detector = None
        
        self.tts = TTSManager()
        
        self.setup_ui()
        
        self.center_window()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.WIDTH // 2)
        y = (self.winfo_screenheight() // 2) - (self.HEIGHT // 2)
        self.geometry(f'{self.WIDTH}x{self.HEIGHT}+{x}+{y}')
    
    def setup_ui(self):
        self.configure(fg_color=self.background_color)
        
        main_container = ctk.CTkFrame(self, fg_color=self.background_color)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent", height=120)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        logo_frame = ctk.CTkFrame(header_frame, width=80, height=80, 
                                 fg_color=self.primary_color, corner_radius=20)
        logo_frame.pack()
        logo_frame.pack_propagate(False)
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="👋",
            font=ctk.CTkFont(size=40)
        )
        logo_label.pack(expand=True)
    
        title_label = ctk.CTkLabel(
            header_frame,
            text="HearMe",
            font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"),
            text_color=self.primary_color
        )
        title_label.pack(pady=(10, 0))
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Sign Language Detection",
            font=ctk.CTkFont(size=16),
            text_color="#666666"
        )
        subtitle_label.pack()
        
        features_container = ctk.CTkFrame(main_container, fg_color="transparent")
        features_container.pack(fill="both", expand=True)
        
        features = [
            ("📱", "Gesture Detection", "Real-time sign to text", self.open_detection),
            ("🎤", "Speech Conversion", "Speech ↔ Text conversion", self.open_speech),
            ("📚", "Gesture Library", "Learn A-Z signs", self.open_library),
            ("🎓", "Learning Mode", "Practice with feedback", self.open_learning)
        ]
        
        for i, (icon, title, description, command) in enumerate(features):
            card = ctk.CTkFrame(
                features_container,
                height=100,  
                corner_radius=20,
                border_width=1,
                border_color="#E0E0E0",
                fg_color="white"
            )
            card.pack(fill="x", pady=8)
            
            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=20, pady=15)
            
            left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            left_frame.pack(side="left", fill="y", expand=True)
            
            icon_title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
            icon_title_frame.pack(fill="x")
            
            icon_label = ctk.CTkLabel(
                icon_title_frame,
                text=icon,
                font=ctk.CTkFont(size=24),
                text_color=self.primary_color,
                width=40
            )
            icon_label.pack(side="left")
            
            text_frame = ctk.CTkFrame(icon_title_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
            
            title_label = ctk.CTkLabel(
                text_frame,
                text=title,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=self.primary_color,
                anchor="w"
            )
            title_label.pack(fill="x")
            
            desc_label = ctk.CTkLabel(
                text_frame,
                text=description,
                font=ctk.CTkFont(size=14),
                text_color="#666666",
                anchor="w"
            )
            desc_label.pack(fill="x", pady=(2, 0))
            
            arrow_button = ctk.CTkButton(
                content_frame,
                text="→",
                command=command,
                width=40,
                height=40,
                fg_color=self.primary_color,
                hover_color="#1976D2",
                font=ctk.CTkFont(size=20, weight="bold"),
                corner_radius=20
            )
            arrow_button.pack(side="right")
    
    def open_detection(self):
        """Open Gesture Detection window"""
        detection_window = DetectionWindow(self, self.detector, self.tts)
        detection_window.grab_set()
    
    def open_learning(self):
        """Open Learning window"""
        learning_window = LearningWindow(self)
    
    def open_speech(self):
        """Open Speech Text Conversion window"""
        speech_window = SpeechWindow(self, self.tts)
        speech_window.grab_set()
    
    def open_library(self):
        """Open Gesture Library window"""
        library_window = LibraryWindow(self)
        library_window.grab_set()
    
   