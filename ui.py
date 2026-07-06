import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import tkinter as tk
from typing import Callable, Any

# Set dark mode and color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AirLightUI(ctk.CTk):
    def __init__(self, on_exit: Callable, on_reconnect: Callable):
        super().__init__()
        
        self.on_exit = on_exit
        self.on_reconnect = on_reconnect
        
        self.title("AirLight - AI Smart Lighting")
        self.geometry("1100x650")
        self.resizable(False, False)
        
        # Grid layout (1 row, 2 columns)
        self.grid_columnconfigure(0, weight=3) # Camera side
        self.grid_columnconfigure(1, weight=1) # Status side
        self.grid_rowconfigure(0, weight=1)
        
        self._setup_camera_frame()
        self._setup_status_frame()
        self._setup_bottom_frame()
        
        # Keep reference to prevent garbage collection
        self._current_image = None
        
    def _setup_camera_frame(self):
        self.cam_frame = ctk.CTkFrame(self, corner_radius=10)
        self.cam_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Use a standard tkinter Label for the video feed (more reliable for rapid updates)
        self.cam_label = tk.Label(self.cam_frame, bg="#2b2b2b", bd=0, highlightthickness=0)
        self.cam_label.pack(expand=True, fill="both", padx=10, pady=10)
        
    def _setup_status_frame(self):
        self.status_frame = ctk.CTkFrame(self, corner_radius=10)
        self.status_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        
        # Title
        title = ctk.CTkLabel(self.status_frame, text="⚡ AirLight", font=("Roboto", 24, "bold"))
        title.pack(pady=20)
        
        # Labels mapping
        self.labels = {}
        
        self._add_status_row("Gesture:", "None", "gesture")
        self._add_status_row("Brightness:", "100%", "brightness")
        self._add_status_row("Color:", "White", "color")
        self._add_status_row("Power:", "OFF", "power")
        self._add_status_row("FPS:", "0", "fps")
        self._add_status_row("Bulb Status:", "Disconnected", "bulb")
        
    def _add_status_row(self, title: str, default_val: str, key: str):
        frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=10)
        
        lbl_title = ctk.CTkLabel(frame, text=title, font=("Roboto", 16))
        lbl_title.pack(side="left")
        
        lbl_val = ctk.CTkLabel(frame, text=default_val, font=("Roboto", 16, "bold"))
        lbl_val.pack(side="right")
        
        self.labels[key] = lbl_val
        
    def _setup_bottom_frame(self):
        self.bottom_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        self.bottom_frame.pack(fill="x", side="bottom", pady=20)
        
        btn_reconnect = ctk.CTkButton(self.bottom_frame, text="Reconnect", command=self.on_reconnect)
        btn_reconnect.pack(pady=10)
        
        btn_exit = ctk.CTkButton(self.bottom_frame, text="Exit", command=self.on_exit, fg_color="#C0392B", hover_color="#922B21")
        btn_exit.pack(pady=10)
        
    def update_frame(self, cv_img: Any):
        """Updates the video feed using standard tkinter PhotoImage for reliability."""
        try:
            # Convert BGR to RGB
            cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            
            # Resize to fit the label area
            cv_img = cv2.resize(cv_img, (640, 480))
            
            # Convert to PIL Image, then to tkinter PhotoImage
            pil_img = Image.fromarray(cv_img)
            photo = ImageTk.PhotoImage(image=pil_img)
            
            # Update label
            self.cam_label.configure(image=photo)
            self._current_image = photo  # Keep reference to prevent GC
        except Exception as e:
            pass  # Skip frame on error, next frame will render
        
    def show_error(self, message: str):
        """Displays an error message in the camera frame."""
        self.cam_label.configure(image="", text=message, fg="red", font=("Roboto", 30, "bold"))
        self._current_image = None
        
    def update_status(self, key: str, value: str):
        """Updates a status text."""
        if key in self.labels:
            self.labels[key].configure(text=str(value))
