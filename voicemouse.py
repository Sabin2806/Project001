import speech_recognition as sr
import pyautogui
import tkinter as tk
from tkinter import ttk, scrolledtext
from threading import Thread
import math

class VoiceControlledMouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Controlled Mouse")
        self.root.geometry("800x600")
        
        # Initialize recognizer
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.current_command = ""
        self.movement_speed = 50
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Mouse simulation variables
        self.virtual_mouse_pos = [400, 300]  # Center of our canvas
        self.mouse_pressed = False
        self.scroll_direction = 0
        
        # Create GUI elements
        self.create_widgets()
        
        # Safety feature
        pyautogui.FAILSAFE = True
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Voice Controlled Mouse", font=('Helvetica', 16))
        title_label.pack(pady=10)
        
        # Status and control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Status: Ready", foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Speed control
        speed_frame = ttk.Frame(control_frame)
        speed_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_scale = ttk.Scale(speed_frame, from_=10, to=200, 
                                   command=lambda e: self.update_speed(),
                                   value=self.movement_speed)
        self.speed_scale.pack(side=tk.LEFT)
        self.speed_value = ttk.Label(speed_frame, text=str(self.movement_speed))
        self.speed_value.pack(side=tk.LEFT)
        
        # Mouse visualization canvas
        self.canvas = tk.Canvas(main_frame, width=600, height=300, bg='white', 
                               highlightthickness=1, highlightbackground="black")
        self.canvas.pack(pady=10)
        
        # Draw screen representation
        self.draw_screen_elements()
        
        # Command display
        command_frame = ttk.Frame(main_frame)
        command_frame.pack(fill=tk.X, pady=5)
        
        self.command_display = ttk.Label(command_frame, text="Last Command: None", 
                                       font=('Helvetica', 12), wraplength=600)
        self.command_display.pack()
        
        # Log area
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, width=80, height=8, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Listening", command=self.start_listening)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Listening", command=self.stop_listening, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Help section
        help_frame = ttk.LabelFrame(main_frame, text="Available Commands", padding="5")
        help_frame.pack(fill=tk.X, pady=5)
        
        help_text = """
        Movement: move left/right/up/down | Clicks: click/double click/right click
        Scrolling: scroll up/down | Dragging: drag/release | Exit: stop
        """
        help_label = ttk.Label(help_frame, text=help_text, justify=tk.LEFT)
        help_label.pack(anchor=tk.W)
        
    def draw_screen_elements(self):
        """Draw initial elements on the canvas"""
        self.canvas.delete("all")
        
        # Draw screen representation
        self.canvas.create_rectangle(10, 10, 590, 290, outline='gray', dash=(2,2))
        
        # Draw mouse pointer (triangle)
        self.mouse_pointer = self.canvas.create_polygon(
            self.virtual_mouse_pos[0], self.virtual_mouse_pos[1],
            self.virtual_mouse_pos[0]-10, self.virtual_mouse_pos[1]+20,
            self.virtual_mouse_pos[0]+10, self.virtual_mouse_pos[1]+20,
            fill='red', outline='black')
            
        # Draw click indicator
        self.click_indicator = self.canvas.create_oval(0, 0, 0, 0, outline='', fill='')
        
        # Draw scroll indicator
        self.scroll_indicator = self.canvas.create_text(0, 0, text="", font=('Arial', 10))
        
    def update_mouse_display(self):
        """Update the visual representation of the mouse"""
        # Update mouse position
        self.canvas.coords(self.mouse_pointer,
                          self.virtual_mouse_pos[0], self.virtual_mouse_pos[1],
                          self.virtual_mouse_pos[0]-10, self.virtual_mouse_pos[1]+20,
                          self.virtual_mouse_pos[0]+10, self.virtual_mouse_pos[1]+20)
        
        # Show click effect if pressed
        if self.mouse_pressed:
            self.canvas.coords(self.click_indicator,
                             self.virtual_mouse_pos[0]-15, self.virtual_mouse_pos[1]-15,
                             self.virtual_mouse_pos[0]+15, self.virtual_mouse_pos[1]+15)
            self.canvas.itemconfig(self.click_indicator, fill='blue', outline='black')
        else:
            self.canvas.coords(self.click_indicator, 0, 0, 0, 0)
        
        # Show scroll effect if scrolling
        if self.scroll_direction != 0:
            scroll_text = "↑" if self.scroll_direction > 0 else "↓"
            self.canvas.coords(self.scroll_indicator, 
                             self.virtual_mouse_pos[0], self.virtual_mouse_pos[1]-30)
            self.canvas.itemconfig(self.scroll_indicator, text=scroll_text, fill='green')
            self.scroll_direction = 0  # Reset after showing
        else:
            self.canvas.itemconfig(self.scroll_indicator, text="")
    
    def update_speed(self):
        """Update movement speed from slider"""
        self.movement_speed = int(self.speed_scale.get())
        self.speed_value.config(text=str(self.movement_speed))
        
    def log_message(self, message):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.configure(state='disabled')
        self.log_area.see(tk.END)
        
    def update_status(self, status, color="black"):
        self.status_label.config(text=f"Status: {status}", foreground=color)
        
    def update_command_display(self, command):
        self.current_command = command
        self.command_display.config(text=f"Last Command: {command}")
        
    def execute_command(self, command):
        """Execute mouse commands based on voice input"""
        command = command.lower()
        self.update_command_display(command)
        self.log_message(f"Executing: {command}")
        
        try:
            if "move left" in command:
                self.virtual_mouse_pos[0] = max(20, self.virtual_mouse_pos[0] - self.movement_speed)
                pyautogui.move(-self.movement_speed, 0)
            elif "move right" in command:
                self.virtual_mouse_pos[0] = min(580, self.virtual_mouse_pos[0] + self.movement_speed)
                pyautogui.move(self.movement_speed, 0)
            elif "move up" in command:
                self.virtual_mouse_pos[1] = max(20, self.virtual_mouse_pos[1] - self.movement_speed)
                pyautogui.move(0, -self.movement_speed)
            elif "move down" in command:
                self.virtual_mouse_pos[1] = min(280, self.virtual_mouse_pos[1] + self.movement_speed)
                pyautogui.move(0, self.movement_speed)
            elif "click" in command:
                self.mouse_pressed = True
                self.update_mouse_display()
                pyautogui.click()
                self.root.after(200, lambda: self.reset_click())
            elif "double click" in command:
                self.mouse_pressed = True
                self.update_mouse_display()
                pyautogui.doubleClick()
                self.root.after(200, lambda: self.reset_click())
            elif "right click" in command:
                self.mouse_pressed = True
                self.update_mouse_display()
                pyautogui.rightClick()
                self.root.after(200, lambda: self.reset_click())
            elif "scroll up" in command:
                self.scroll_direction = 1
                pyautogui.scroll(10)
            elif "scroll down" in command:
                self.scroll_direction = -1
                pyautogui.scroll(-10)
            elif "drag" in command:
                self.mouse_pressed = True
                pyautogui.mouseDown()
            elif "release" in command:
                self.mouse_pressed = False
                pyautogui.mouseUp()
            elif "stop" in command:
                self.stop_listening()
                return False
            else:
                self.log_message("Command not recognized")
        except Exception as e:
            self.log_message(f"Error executing command: {e}")
        
        self.update_mouse_display()
        return True
    
    def reset_click(self):
        self.mouse_pressed = False
        self.update_mouse_display()
    
    def listen_for_commands(self):
        """Listen for voice commands using microphone"""
        with sr.Microphone() as source:
            self.log_message("Calibrating microphone...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.log_message("Ready for voice commands. Say 'stop' to exit.")
            self.update_status("Listening", "green")
            
            while self.is_listening:
                try:
                    self.log_message("Listening...")
                    audio = self.recognizer.listen(source, timeout=3)
                    self.log_message("Processing command...")
                    
                    # Recognize speech using Google Speech Recognition
                    command = self.recognizer.recognize_google(audio)
                    self.log_message(f"You said: {command}")
                    
                    self.execute_command(command)
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    self.log_message("Could not understand audio")
                except sr.RequestError as e:
                    self.log_message(f"Could not request results; {e}")
                except Exception as e:
                    self.log_message(f"Error: {e}")
        
        self.update_status("Stopped", "red")
        self.log_message("Voice control stopped")
    
    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.update_status("Starting...", "orange")
            
            # Start listening in a separate thread
            self.listening_thread = Thread(target=self.listen_for_commands)
            self.listening_thread.daemon = True
            self.listening_thread.start()
    
    def stop_listening(self):
        if self.is_listening:
            self.is_listening = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.update_status("Stopping...", "orange")
            
            # Wait for the thread to finish
            if hasattr(self, 'listening_thread'):
                self.listening_thread.join(timeout=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceControlledMouseApp(root)
    root.mainloop()
