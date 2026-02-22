import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import os

class LibraryWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.WIDTH = 390
        self.HEIGHT = 844
        
        self.title("HearMe - Library")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.resizable(False, False)
        
        self.primary_color = "#2196F3"
        self.white = "#FFFFFF"
        self.gray = "#F5F5F5"
        self.dark_gray = "#666666"
  
        self.setup_ui()
        
        self.center_window()
    
    def center_window(self):
        """Center window on screen"""
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
            text="Sign Library",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.primary_color
        )
        title_label.pack(side="left", padx=20)

        instructions = ctk.CTkLabel(
            self.main_container,
            text="Tap any letter to learn its sign",
            font=ctk.CTkFont(size=14),
            text_color=self.dark_gray
        )
        instructions.pack(anchor="w", pady=(0, 15))

        letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", 
                  "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        
        grid_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        grid_container.pack(fill="both", expand=True)
        
        for i, letter in enumerate(letters):
            row = i // 3
            col = i % 3
            
            card = ctk.CTkFrame(
                grid_container,
                width=100,
                height=120,
                corner_radius=15,
                fg_color=self.white,
                border_width=1,
                border_color="#E0E0E0"
            )
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            card.grid_propagate(False)
            
            grid_container.grid_columnconfigure(col, weight=1, uniform="col")
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=10, pady=10)
            
            letter_label = ctk.CTkLabel(
                content,
                text=letter,
                font=ctk.CTkFont(size=32, weight="bold"),
                text_color=self.primary_color
            )
            letter_label.pack(expand=True)
            
            sign_label = ctk.CTkLabel(
                content,
                text=f"Sign '{letter}'",
                font=ctk.CTkFont(size=12),
                text_color=self.dark_gray
            )
            sign_label.pack()
            
            card.bind("<Button-1>", lambda e, l=letter: self.show_sign_detail(l))
            letter_label.bind("<Button-1>", lambda e, l=letter: self.show_sign_detail(l))
            sign_label.bind("<Button-1>", lambda e, l=letter: self.show_sign_detail(l))
    
    def show_sign_detail(self, letter):
        """Show detailed view for a sign"""
        detail_window = SignDetailWindow(self, letter)
        detail_window.grab_set()


class SignDetailWindow(ctk.CTkToplevel):
    """Popup window showing sign details"""
    
    def __init__(self, parent, letter):
        super().__init__(parent)
        
        self.WIDTH = 300
        self.HEIGHT = 400
        
        self.title(f"Sign for '{letter}'")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.resizable(False, False)
        
        self.primary_color = "#2196F3"
        self.white = "#FFFFFF"
        
        self.setup_ui(letter)
        
        self.center_window()
        
        self.grab_set()
    
    def center_window(self):
        """Center window on parent"""
        self.update_idletasks()
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        x = parent_x + (parent_width - self.WIDTH) // 2
        y = parent_y + (parent_height - self.HEIGHT) // 2
        
        self.geometry(f'+{x}+{y}')
    
    def setup_ui(self, letter):
        self.configure(fg_color=self.white)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            content,
            text=letter,
            font=ctk.CTkFont(size=72, weight="bold"),
            text_color=self.primary_color
        ).pack(pady=(10, 20))
        
        image_frame = ctk.CTkFrame(
            content,
            width=150,
            height=150,
            corner_radius=75,
            fg_color=self.primary_color + "20"  # 20 = 12% opacity
        )
        image_frame.pack(pady=(0, 20))
        image_frame.pack_propagate(False)

        ctk.CTkLabel(
            image_frame,
            text="👋",
            font=ctk.CTkFont(size=60)
        ).pack(expand=True)

        description = self.get_sign_description(letter)
        desc_label = ctk.CTkLabel(
            content,
            text=description,
            font=ctk.CTkFont(size=14),
            text_color="#666666",
            wraplength=250,
            justify="center"
        )
        desc_label.pack(pady=(0, 20))
        
        close_button = ctk.CTkButton(
            content,
            text="Close",
            command=self.destroy,
            height=40,
            fg_color=self.primary_color,
            hover_color="#1976D2",
            font=ctk.CTkFont(size=15)
        )
        close_button.pack(fill="x", pady=(10, 0))
    
    def get_sign_description(self, letter):
        """Get description for a sign"""
        descriptions = {
            'A': 'Closed fist with thumb resting alongside index finger',
            'B': 'Flat hand with fingers together, thumb across palm',
            'C': 'Curved hand shaped like the letter C',
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
        return descriptions.get(letter, f"American Sign Language for '{letter}'")