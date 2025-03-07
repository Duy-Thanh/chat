# # chat_gui.py
# import customtkinter as ctk
# import datetime
# from PIL import Image
# import os
# import pystray
# import threading
# import ewmh

# class ModernChatGUI:
#     def __init__(self):
#         # Set theme and color scheme
#         ctk.set_appearance_mode("dark")
#         ctk.set_default_color_theme("blue")
        
#         self.window = ctk.CTk()
#         self.window.title("Secure Chat")
#         self.window.geometry("1000x700")
#         self.window.minsize(800, 600)  # Set minimum window size
        
#         # Enhanced color scheme
#         self.colors = {
#             "primary": "#2B5BF1",       # Vibrant blue
#             "primary_hover": "#1E45D1",  # Darker blue
#             "secondary": "#2D2D2D",      # Dark gray
#             "accent": "#00C2FF",         # Bright cyan
#             "bg_dark": "#1A1A1A",        # Very dark gray
#             "bg_light": "#2D2D2D",       # Medium dark gray
#             "bg_input": "#363636",       # Lighter input background
#             "text": "#FFFFFF",           # White text
#             "text_secondary": "#A0A0A0", # Light gray text
#             "border": "#404040",         # Border color
#             "success": "#2ECC71",        # Green
#             "error": "#E74C3C"           # Red
#         }
        
#         # Store initial position and state
#         self.window_state = "normal"
#         self.initial_position = None
#         self.tray_icon = None
        
#         # Initialize EWMH
#         self.ewmh = ewmh.EWMH()
        
#         # Create main layout frames
#         self.create_layout_frames()
        
#         # Create content
#         self.create_chat_header()
#         self.create_sidebar()
#         self.create_chat_area()
#         self.create_input_area()
        
#         # Initialize system tray
#         self.setup_system_tray()
        
#         # Bind resize event
#         self.window.bind("<Configure>", self.on_window_configure)
        
#         # Wait for window to be created
#         self.window.update()
        
#         # Set window type hints
#         self.set_window_hints()
        
#         # Bind window close event
#         self.window.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)
        
#     def set_window_hints(self):
#         try:
#             # Get window ID
#             window_id = self.window.winfo_id()
#             win = self.ewmh.display.create_resource_object('window', window_id)
            
#             # Set window type to normal
#             self.ewmh._setProperty('_NET_WM_WINDOW_TYPE', 
#                                  [self.ewmh.display.get_atom('_NET_WM_WINDOW_TYPE_NORMAL')], 
#                                  win)
            
#             # Allow window to be minimized
#             self.ewmh._setProperty('_NET_WM_ALLOWED_ACTIONS', [
#                 self.ewmh.display.get_atom("_NET_WM_ACTION_MINIMIZE"),
#                 self.ewmh.display.get_atom("_NET_WM_ACTION_MAXIMIZE"),
#                 self.ewmh.display.get_atom("_NET_WM_ACTION_CLOSE")
#             ], win)
            
#             self.ewmh.display.flush()
#         except Exception as e:
#             print(f"Error setting window hints: {e}")
        
#     def minimize_window(self):
#         try:
#             window_id = self.window.winfo_id()
#             win = self.ewmh.display.create_resource_object('window', window_id)
#             self.ewmh._setProperty('_NET_WM_STATE', 
#                                  [self.ewmh.display.get_atom('_NET_WM_STATE_HIDDEN')], 
#                                  win)
#             self.ewmh.display.flush()
#         except Exception as e:
#             print(f"Error minimizing window: {e}")
            
#     def restore_window(self):
#         try:
#             window_id = self.window.winfo_id()
#             win = self.ewmh.display.create_resource_object('window', window_id)
#             self.ewmh._setProperty('_NET_WM_STATE', [], win)  # Clear states
#             self.ewmh.display.flush()
#             self.window.deiconify()
#             self.window.attributes('-topmost', True)
#             self.window.update()
#             self.window.attributes('-topmost', False)
#         except Exception as e:
#             print(f"Error restoring window: {e}")

#     def quit_app(self, icon=None):
#         if self.tray_icon:
#             self.tray_icon.stop()
#         self.window.quit()

#     def create_layout_frames(self):
#         # Left frame for sidebar
#         self.left_frame = ctk.CTkFrame(
#             self.window,
#             width=280,
#             fg_color="transparent"
#         )
#         self.left_frame.pack(side="left", fill="y", padx=10, pady=10)
#         self.left_frame.pack_propagate(False)
        
#         # Right frame for chat area
#         self.right_frame = ctk.CTkFrame(
#             self.window,
#             fg_color="transparent"
#         )
#         self.right_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

#     def create_chat_header(self):
#         # Chat header with user info
#         self.chat_header = ctk.CTkFrame(
#             self.right_frame,
#             height=60,
#             fg_color=self.colors["bg_dark"],
#             corner_radius=10
#         )
#         self.chat_header.pack(fill="x", pady=(0, 5))
#         self.chat_header.pack_propagate(False)
        
#         # Current chat info
#         self.chat_info = ctk.CTkFrame(
#             self.chat_header,
#             fg_color="transparent"
#         )
#         self.chat_info.pack(side="left", fill="y", padx=15)
        
#         self.chat_title = ctk.CTkLabel(
#             self.chat_info,
#             text="You: Test",
#             font=ctk.CTkFont(size=16, weight="bold"),
#             text_color=self.colors["text"]
#         )
#         self.chat_title.pack(anchor="w", pady=(10, 0))
        
#         self.chat_status = ctk.CTkLabel(
#             self.chat_info,
#             text="🟢 Online",
#             font=ctk.CTkFont(size=12),
#             text_color=self.colors["text_secondary"]
#         )
#         self.chat_status.pack(anchor="w", pady=(2, 10))
        
#         # Right controls
#         self.chat_controls = ctk.CTkFrame(
#             self.chat_header,
#             fg_color="transparent"
#         )
#         self.chat_controls.pack(side="right", fill="y", padx=10)
        
#         # Search in chat
#         self.chat_search = ctk.CTkEntry(
#             self.chat_controls,
#             width=200,
#             placeholder_text="Search in chat...",
#             fg_color=self.colors["bg_input"],
#             border_width=0,
#             height=32
#         )
#         self.chat_search.pack(side="left", padx=5, pady=14)
        
#         # Call button
#         self.call_btn = ctk.CTkButton(
#             self.chat_controls,
#             text="📞",
#             width=36,
#             height=36,
#             corner_radius=18,
#             fg_color=self.colors["primary"],
#             hover_color=self.colors["primary_hover"],
#             command=self.start_call
#         )
#         self.call_btn.pack(side="left", padx=5)
        
#         # Video call button
#         self.video_btn = ctk.CTkButton(
#             self.chat_controls,
#             text="📹",
#             width=36,
#             height=36,
#             corner_radius=18,
#             fg_color=self.colors["primary"],
#             hover_color=self.colors["primary_hover"],
#             command=self.start_video_call
#         )
#         self.video_btn.pack(side="left", padx=5)

#     def create_sidebar(self):
#         # Profile and chats list
#         self.sidebar = ctk.CTkFrame(
#             self.left_frame,
#             fg_color=self.colors["bg_light"],
#             corner_radius=10
#         )
#         self.sidebar.pack(fill="both", expand=True)
        
#         # Profile section
#         self.profile_frame = ctk.CTkFrame(
#             self.sidebar,
#             fg_color=self.colors["bg_dark"],
#             corner_radius=8
#         )
#         self.profile_frame.pack(fill="x", padx=10, pady=10)
        
#         # Profile info with avatar
#         self.avatar_label = ctk.CTkLabel(
#             self.profile_frame,
#             text="👤",
#             font=ctk.CTkFont(size=32),
#             width=50,
#             height=50
#         )
#         self.avatar_label.pack(side="left", padx=10, pady=10)
        
#         self.profile_info = ctk.CTkFrame(
#             self.profile_frame,
#             fg_color="transparent"
#         )
#         self.profile_info.pack(side="left", fill="x", expand=True, pady=10)
        
#         self.profile_label = ctk.CTkLabel(
#             self.profile_info,
#             text="User Name",
#             font=ctk.CTkFont(size=16, weight="bold"),
#             text_color=self.colors["text"]
#         )
#         self.profile_label.pack(anchor="w")
        
#         self.status_label = ctk.CTkLabel(
#             self.profile_info,
#             text="🟢 Online",
#             font=ctk.CTkFont(size=13),
#             text_color=self.colors["text_secondary"]
#         )
#         self.status_label.pack(anchor="w")
        
#         # Chats section
#         self.chats_label = ctk.CTkLabel(
#             self.sidebar,
#             text="Recent Chats",
#             font=ctk.CTkFont(size=14, weight="bold"),
#             text_color=self.colors["text_secondary"]
#         )
#         self.chats_label.pack(anchor="w", padx=15, pady=(20, 10))
        
#         # Add some dummy chats
#         self.create_chat_item("Alice", "Hello! How are you?", "10:30")
#         self.create_chat_item("Bob", "Did you see the new update?", "09:45")
#         self.create_chat_item("Charlie", "Meeting at 3 PM", "Yesterday")

#     def create_chat_item(self, name, message, time):
#         chat_item = ctk.CTkFrame(
#             self.sidebar,
#             fg_color="transparent",
#             height=70
#         )
#         chat_item.pack(fill="x", padx=10, pady=2)
#         chat_item.pack_propagate(False)
        
#         # Avatar
#         avatar = ctk.CTkLabel(
#             chat_item,
#             text="👤",
#             font=ctk.CTkFont(size=24),
#             width=40,
#             height=40
#         )
#         avatar.pack(side="left", padx=10)
        
#         # Chat info
#         info_frame = ctk.CTkFrame(
#             chat_item,
#             fg_color="transparent"
#         )
#         info_frame.pack(side="left", fill="both", expand=True, pady=5)
        
#         name_time = ctk.CTkFrame(
#             info_frame,
#             fg_color="transparent"
#         )
#         name_time.pack(fill="x")
        
#         # Name
#         ctk.CTkLabel(
#             name_time,
#             text=name,
#             font=ctk.CTkFont(size=14, weight="bold"),
#             text_color=self.colors["text"]
#         ).pack(side="left")
        
#         # Time
#         ctk.CTkLabel(
#             name_time,
#             text=time,
#             font=ctk.CTkFont(size=12),
#             text_color=self.colors["text_secondary"]
#         ).pack(side="right")
        
#         # Message preview
#         ctk.CTkLabel(
#             info_frame,
#             text=message,
#             font=ctk.CTkFont(size=12),
#             text_color=self.colors["text_secondary"]
#         ).pack(anchor="w")

#     def create_chat_area(self):
#         # Chat messages area with modern styling
#         self.chat_frame = ctk.CTkFrame(
#             self.right_frame,
#             fg_color=self.colors["bg_dark"],
#             corner_radius=10
#         )
#         self.chat_frame.pack(fill="both", expand=True)
        
#         # Messages display with custom styling
#         self.chat_display = ctk.CTkTextbox(
#             self.chat_frame,
#             font=ctk.CTkFont(size=13),
#             fg_color=self.colors["bg_light"],
#             text_color=self.colors["text"],
#             corner_radius=10,
#             border_width=1,
#             border_color=self.colors["border"]
#         )
#         self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)
        
#         # Configure message bubble tags
#         self.chat_display.tag_config(
#             "sent_message",
#             justify="right",
#             spacing1=10,
#             spacing3=5
#         )
#         self.chat_display.tag_config(
#             "received_message",
#             justify="left",
#             spacing1=10,
#             spacing3=5
#         )
#         self.chat_display.tag_config(
#             "timestamp",
#             justify="center",
#             foreground=self.colors["text_secondary"]
#         )
#         self.chat_display.tag_config(
#             "bubble_sent",
#             background=self.colors["primary"],
#             foreground=self.colors["text"],
#             relief="solid",
#             borderwidth=0
#         )
#         self.chat_display.tag_config(
#             "bubble_received",
#             background=self.colors["secondary"],
#             foreground=self.colors["text"],
#             relief="solid",
#             borderwidth=0
#         )
        
#         # Make text display read-only
#         self.chat_display.configure(state="disabled")

#     def create_input_area(self):
#         # Modern input area with attachments
#         self.input_frame = ctk.CTkFrame(
#             self.chat_frame,
#             height=70,
#             fg_color=self.colors["bg_light"],
#             corner_radius=10
#         )
#         self.input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
#         # Attachment button
#         self.attach_btn = ctk.CTkButton(
#             self.input_frame,
#             text="📎",
#             width=40,
#             height=40,
#             corner_radius=20,
#             fg_color="transparent",
#             hover_color=self.colors["secondary"],
#             command=self.attach_file
#         )
#         self.attach_btn.pack(side="left", padx=(10, 5), pady=15)
        
#         # Emoji button
#         self.emoji_btn = ctk.CTkButton(
#             self.input_frame,
#             text="😊",
#             width=40,
#             height=40,
#             corner_radius=20,
#             fg_color="transparent",
#             hover_color=self.colors["secondary"],
#             command=self.show_emoji_picker
#         )
#         self.emoji_btn.pack(side="left", padx=5, pady=15)
        
#         # Message input with placeholder
#         self.message_input = ctk.CTkTextbox(
#             self.input_frame,
#             height=40,
#             font=ctk.CTkFont(size=13),
#             fg_color=self.colors["bg_input"],
#             text_color=self.colors["text"],
#             corner_radius=20,
#             border_width=1,
#             border_color=self.colors["border"]
#         )
#         self.message_input.pack(side="left", fill="x", expand=True, padx=5, pady=15)
        
#         # Send button with animation effect
#         self.send_btn = ctk.CTkButton(
#             self.input_frame,
#             text="Send ➤",
#             width=100,
#             height=40,
#             corner_radius=20,
#             fg_color=self.colors["primary"],
#             hover_color=self.colors["primary_hover"],
#             font=ctk.CTkFont(size=13, weight="bold"),
#             command=self.send_message
#         )
#         self.send_btn.pack(side="right", padx=10, pady=15)

#     def send_message(self):
#         message = self.message_input.get("1.0", "end-1c").strip()
#         if message:
#             # Enable text widget for updating
#             self.chat_display.configure(state="normal")
            
#             # Add timestamp
#             timestamp = datetime.datetime.now().strftime("%H:%M")
#             self.chat_display.insert("end", f"\n{timestamp}\n", "timestamp")
            
#             # Add padding for right alignment
#             padding = " " * 50
            
#             # Add message with bubble styling
#             self.chat_display.insert("end", f"{padding}You: {message}\n", ("sent_message", "bubble_sent"))
            
#             # Add some visual spacing
#             self.chat_display.insert("end", "\n")
            
#             # Scroll to bottom and clear input
#             self.chat_display.see("end")
#             self.chat_display.configure(state="disabled")
#             self.message_input.delete("1.0", "end")
            
#             # Simulate received message (for testing)
#             self.after_received_message(f"Echo: {message}")

#     def after_received_message(self, message):
#         # Simulate delay for realism
#         self.window.after(1000, lambda: self.receive_message(message))

#     def receive_message(self, message):
#         # Enable text widget for updating
#         self.chat_display.configure(state="normal")
        
#         # Add timestamp
#         timestamp = datetime.datetime.now().strftime("%H:%M")
#         self.chat_display.insert("end", f"\n{timestamp}\n", "timestamp")
        
#         # Add message with bubble styling
#         self.chat_display.insert("end", f"{message}\n", ("received_message", "bubble_received"))
        
#         # Add some visual spacing
#         self.chat_display.insert("end", "\n")
        
#         # Scroll to bottom
#         self.chat_display.see("end")
#         self.chat_display.configure(state="disabled")

#     def handle_return(self, event):
#         # Send message on Enter, allow Shift+Enter for new line
#         if not event.state & 0x1:  # Shift not pressed
#             self.send_message()
#             return "break"  # Prevents default Enter behavior
            
#     def attach_file(self):
#         # TODO: Implement file attachment
#         pass

#     def show_emoji_picker(self):
#         # TODO: Implement emoji picker
#         pass

#     def start_call(self):
#         # TODO: Implement call functionality
#         pass

#     def start_video_call(self):
#         # TODO: Implement video call functionality
#         pass

#     def on_window_configure(self, event=None):
#         # Update layout when window is resized
#         if event and event.widget == self.window:
#             # Ensure minimum sidebar width
#             min_sidebar_width = 280
#             if self.window.winfo_width() > 1000:
#                 self.sidebar.configure(width=min_sidebar_width)
            
#             # Adjust chat area width
#             chat_width = self.window.winfo_width() - min_sidebar_width - 30
#             if chat_width > 400:  # Minimum chat area width
#                 self.chat_frame.configure(width=chat_width)

#     def setup_system_tray(self):
#         # Create a simple icon
#         icon_image = Image.new('RGB', (64, 64), color='blue')
#         menu = (
#             pystray.MenuItem('Show', self.restore_window),
#             pystray.MenuItem('Exit', self.quit_app)
#         )
#         self.tray_icon = pystray.Icon(
#             "secure_chat",
#             icon_image,
#             "Secure Chat",
#             menu=pystray.Menu(*menu)
#         )
        
#         # Start the tray icon in a separate thread
#         threading.Thread(target=self.tray_icon.run, daemon=True).start()

#     def minimize_to_tray(self):
#         self.window.withdraw()  # Hide the window
        
#     def run(self):
#         self.window.mainloop()

# if __name__ == "__main__":
#     app = ModernChatGUI()
#     app.run()