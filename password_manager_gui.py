import sys
sys.path.append("/usr/local/lib/python3.10/site-packages")
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import string
import random
import pyperclip
from theme import Theme
from utils import DatabaseManager, EncryptionManager
import json
from datetime import datetime
import os
import bcrypt
import sqlite3
import math
import threading

class Sparkle:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = random.randint(2, 4)
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, 2 * math.pi)
        self.color = random.choice([Theme.COLORS["sparkle"], Theme.COLORS["sparkle_alt"]])
        self.alpha = 1.0
        self.fade_speed = random.uniform(0.02, 0.05)
        
        # Create the sparkle on canvas
        self.id = self.canvas.create_oval(
            x - self.size, y - self.size,
            x + self.size, y + self.size,
            fill=self.color, outline=self.color
        )

    def update(self):
        # Update position with slight random movement
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed + 0.5  # Add slight downward drift
        
        # Add some wobble
        self.angle += random.uniform(-0.1, 0.1)
        
        # Update alpha (fade out)
        self.alpha -= self.fade_speed
        
        if self.alpha <= 0:
            self.canvas.delete(self.id)
            return False
        
        # Move the sparkle
        self.canvas.move(
            self.id,
            math.cos(self.angle) * self.speed,
            math.sin(self.angle) * self.speed + 0.5
        )
        
        return True

class SparkleCanvas:
    def __init__(self, parent):
        self.canvas = tk.Canvas(
            parent,
            highlightthickness=0,
            bg=Theme.COLORS["background"]
        )
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.sparkles = []
        self.parent = parent
        self.is_running = True
        self.update_sparkles()
        self.generate_sparkles()

    def generate_sparkles(self):
        if not self.is_running:
            return
            
        # Generate new sparkles randomly
        if random.random() < 0.2:  # Adjust probability to control density
            x = random.randint(0, self.parent.winfo_width())
            y = random.randint(0, self.parent.winfo_height())
            self.sparkles.append(Sparkle(self.canvas, x, y))
            
        self.parent.after(50, self.generate_sparkles)

    def update_sparkles(self):
        if not self.is_running:
            return
            
        # Update existing sparkles
        self.sparkles = [sparkle for sparkle in self.sparkles if sparkle.update()]
        self.parent.after(16, self.update_sparkles)  # ~60 FPS

    def stop(self):
        self.is_running = False
        self.canvas.destroy()

class PasswordManagerGUI:
    def __init__(self):
        # Initialize database in a separate thread
        self.db_manager = None
        self.encryption_manager = None
        
        # Create and configure the main window immediately
        self.root = ctk.CTk()
        self.root.title("Secure Password Manager")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Center window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        self.root.geometry(f"800x600+{x}+{y}")

        # Set theme
        self.root.configure(fg_color=Theme.COLORS["background"])
        
        # Create main container
        self.main_frame = ctk.CTkFrame(self.root, **Theme.get_frame_style("main"))
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Show loading screen
        self.show_loading_screen()
        
        # Initialize database in background
        threading.Thread(target=self.initialize_database, daemon=True).start()

    def show_loading_screen(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Loading frame
        loading_frame = ctk.CTkFrame(self.main_frame, **Theme.get_frame_style("card"))
        loading_frame.pack(expand=True, padx=50, pady=50)

        # Loading text
        loading_label = ctk.CTkLabel(
            loading_frame,
            text="Loading...",
            font=("Helvetica", 20, "bold"),
            text_color="#000000"
        )
        loading_label.pack(pady=20)

        # Create loading animation
        self.loading_dots = ""
        self.update_loading_animation(loading_label)

    def update_loading_animation(self, label):
        if len(self.loading_dots) >= 3:
            self.loading_dots = ""
        else:
            self.loading_dots += "."
        
        label.configure(text=f"Loading{self.loading_dots}")
        
        # Continue animation if database isn't ready
        if not self.db_manager:
            self.root.after(500, lambda: self.update_loading_animation(label))

    def initialize_database(self):
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Switch to login screen
        self.root.after(0, self.show_login_screen)

    def show_login_screen(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create a canvas for login animations
        self.login_canvas = tk.Canvas(
            self.main_frame,
            highlightthickness=0,
            bg=Theme.COLORS["background"]
        )
        self.login_canvas.pack(fill="both", expand=True)

        # Login frame
        login_frame = ctk.CTkFrame(self.login_canvas, **Theme.get_frame_style("card"))
        
        # Calculate center position based on canvas size
        def center_frame(event=None):
            canvas_width = self.login_canvas.winfo_width()
            canvas_height = self.login_canvas.winfo_height()
            frame_width = 400  # Fixed width for login frame
            frame_height = 350  # Fixed height for login frame
            x = (canvas_width - frame_width) // 2
            y = (canvas_height - frame_height) // 2
            self.login_canvas.coords(login_frame_window, x + frame_width//2, y + frame_height//2)

        login_frame_window = self.login_canvas.create_window(
            0, 0,  # Initial position, will be centered
            window=login_frame,
            anchor="center",
            width=400,
            height=350
        )

        # Bind resize event to recenter the frame
        self.login_canvas.bind("<Configure>", center_frame)

        # Title with glow effect
        title_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        title_frame.pack(pady=20)

        title_label = ctk.CTkLabel(
            title_frame,
            text="Password Manager Login",
            font=Theme.FONTS["title"],
            text_color="#000000"
        )
        title_label.pack()

        # Username
        username_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="Username",
            width=200,
            **Theme.get_entry_style()
        )
        username_entry.pack(pady=10)

        # Password
        password_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="Password",
            width=200,
            show="•",
            **Theme.get_entry_style()
        )
        password_entry.pack(pady=10)

        # Login button with hover effect
        login_button = ctk.CTkButton(
            login_frame,
            text="Login",
            width=200,
            command=lambda: self.handle_login(username_entry.get(), password_entry.get()),
            **Theme.get_button_style("primary")
        )
        login_button.pack(pady=20)

        # Default credentials label
        info_label = ctk.CTkLabel(
            login_frame,
            text="Default credentials: admin/admin123",
            font=("Helvetica", 10, "bold"),
            text_color="#000000"
        )
        info_label.pack(pady=10)

        # Particle system for login screen
        particles = []
        
        def create_particle():
            size = random.randint(2, 4)
            x = random.randint(0, self.main_frame.winfo_width())
            y = random.randint(0, self.main_frame.winfo_height())
            color = random.choice(['#FFD700', '#FFFFFF'])  # Gold and White
            particle = self.login_canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill=color, outline=color
            )
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2)
            return {
                'id': particle,
                'x': x,
                'y': y,
                'angle': angle,
                'speed': speed,
                'size': size,
                'alpha': 1.0
            }

        def update_particles():
            nonlocal particles
            
            # Create new particles
            if len(particles) < 50 and random.random() < 0.3:
                particles.append(create_particle())

            # Update existing particles
            for particle in particles[:]:
                # Update position
                particle['x'] += math.cos(particle['angle']) * particle['speed']
                particle['y'] += math.sin(particle['angle']) * particle['speed']
                
                # Update angle (create swirling effect)
                particle['angle'] += random.uniform(-0.1, 0.1)
                
                # Move particle
                self.login_canvas.move(
                    particle['id'],
                    math.cos(particle['angle']) * particle['speed'],
                    math.sin(particle['angle']) * particle['speed']
                )
                
                # Check if particle is out of bounds
                pos = self.login_canvas.coords(particle['id'])
                if pos:  # Check if particle still exists
                    if (pos[0] < -10 or pos[2] > self.main_frame.winfo_width() + 10 or
                        pos[1] < -10 or pos[3] > self.main_frame.winfo_height() + 10):
                        self.login_canvas.delete(particle['id'])
                        particles.remove(particle)

            # Continue animation if login screen is still showing
            if self.login_canvas.winfo_exists():
                self.login_canvas.after(16, update_particles)

        # Floating animation for login frame
        float_offset = 0
        float_direction = 1
        
        def update_float_animation():
            nonlocal float_offset, float_direction
            
            # Update floating effect
            float_offset += 0.2 * float_direction
            if abs(float_offset) > 10:  # Max float distance
                float_direction *= -1
            
            # Get current position
            x = self.login_canvas.coords(login_frame_window)[0]
            y = self.login_canvas.coords(login_frame_window)[1]
            
            # Update login frame position with float offset
            self.login_canvas.coords(
                login_frame_window,
                x,  # Keep X position
                y + float_offset - float_offset  # Add floating effect to Y position
            )
            
            # Continue animation if login screen is still showing
            if self.login_canvas.winfo_exists():
                self.login_canvas.after(16, update_float_animation)

        # Start animations
        center_frame()  # Initial centering
        update_particles()
        update_float_animation()

        # Hover effects for buttons using CTkButton's configure method
        def on_button_hover(event):
            login_button.configure(hover_color="#333333")  # Darker shade on hover

        def on_button_leave(event):
            login_button.configure(hover_color=Theme.get_button_style("primary")["hover_color"])  # Reset to original hover color

        login_button.bind("<Enter>", on_button_hover)
        login_button.bind("<Leave>", on_button_leave)

    def handle_login(self, username, password):
        if self.db_manager.verify_user(username, password):
            self.encryption_manager = EncryptionManager(password)
            self.show_main_screen()
        else:
            messagebox.showerror("Error", "Invalid credentials!")

    def show_main_screen(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create left and right panels
        left_panel = ctk.CTkFrame(self.main_frame, **Theme.get_frame_style("card"))
        left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        right_panel = ctk.CTkFrame(self.main_frame, **Theme.get_frame_style("card"))
        right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Left panel - Password Generator
        self.setup_password_generator(left_panel)

        # Right panel - Password Manager
        self.setup_password_manager(right_panel)

    def setup_password_generator(self, parent):
        # Title
        title_label = ctk.CTkLabel(
            parent,
            text="Password Generator",
            font=Theme.FONTS["title"],
            text_color="#000000"
        )
        title_label.pack(pady=20)

        # Options frame
        options_frame = ctk.CTkFrame(parent, **Theme.get_frame_style("card"))
        options_frame.pack(padx=20, pady=10, fill="x")

        # Length slider with value display
        length_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        length_frame.pack(pady=5, fill="x")
        
        length_label = ctk.CTkLabel(length_frame, text="Length:", text_color="#000000")
        length_label.pack(side="left", padx=5)
        
        length_value = tk.StringVar(value="12")
        length_value_label = ctk.CTkLabel(length_frame, textvariable=length_value, text_color="#000000")
        length_value_label.pack(side="right", padx=5)

        def update_length_value(value):
            length_value.set(str(int(float(value))))

        length_slider = ctk.CTkSlider(
            options_frame,
            from_=8,
            to=20,
            number_of_steps=12,
            command=update_length_value,
            button_color="#000000",
            button_hover_color="#333333",
            progress_color="#000000",
            fg_color="#CCCCCC"
        )
        length_slider.set(12)
        length_slider.pack(pady=5)

        # Categories frame with title
        categories_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        categories_frame.pack(pady=10, fill="x")
        
        categories_label = ctk.CTkLabel(
            categories_frame,
            text="Password Categories:",
            font=("Helvetica", 12, "bold"),
            text_color="#000000"
        )
        categories_label.pack(pady=(0, 5))

        # Checkboxes container with two columns
        checkboxes_frame = ctk.CTkFrame(categories_frame, fg_color="transparent")
        checkboxes_frame.pack(fill="x", padx=20)

        # Left column
        left_column = ctk.CTkFrame(checkboxes_frame, fg_color="transparent")
        left_column.pack(side="left", fill="x", expand=True)

        # Right column
        right_column = ctk.CTkFrame(checkboxes_frame, fg_color="transparent")
        right_column.pack(side="right", fill="x", expand=True)

        # Lowercase letters (always enabled)
        use_lowercase = ctk.CTkCheckBox(
            left_column,
            text="Lowercase (a-z)",
            text_color="#000000",
            fg_color="#000000",
            hover_color="#333333",
            border_color="#000000",
            checkmark_color="#FFFFFF"
        )
        use_lowercase.select()
        use_lowercase.configure(state="disabled")  # Always enabled
        use_lowercase.pack(pady=5, anchor="w")

        # Uppercase letters
        use_uppercase = ctk.CTkCheckBox(
            left_column,
            text="Uppercase (A-Z)",
            text_color="#000000",
            fg_color="#000000",
            hover_color="#333333",
            border_color="#000000",
            checkmark_color="#FFFFFF"
        )
        use_uppercase.select()
        use_uppercase.pack(pady=5, anchor="w")

        # Numbers
        use_numbers = ctk.CTkCheckBox(
            right_column,
            text="Numbers (0-9)",
            text_color="#000000",
            fg_color="#000000",
            hover_color="#333333",
            border_color="#000000",
            checkmark_color="#FFFFFF"
        )
        use_numbers.select()
        use_numbers.pack(pady=5, anchor="w")

        # Symbols
        use_symbols = ctk.CTkCheckBox(
            right_column,
            text="Symbols (!@#$%)",
            text_color="#000000",
            fg_color="#000000",
            hover_color="#333333",
            border_color="#000000",
            checkmark_color="#FFFFFF"
        )
        use_symbols.select()
        use_symbols.pack(pady=5, anchor="w")

        # Generated password display
        password_var = tk.StringVar()
        password_entry = ctk.CTkEntry(
            parent,
            textvariable=password_var,
            width=200,
            **Theme.get_entry_style()
        )
        password_entry.pack(pady=20)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(pady=10)

        def generate_password():
            # Always include lowercase as base
            chars = string.ascii_lowercase
            
            # Add selected categories
            if use_uppercase.get(): chars += string.ascii_uppercase
            if use_numbers.get(): chars += string.digits
            if use_symbols.get(): chars += string.punctuation

            # Generate password with at least one character from each selected category
            length = int(length_slider.get())
            password = []
            
            # Always add one lowercase
            password.append(random.choice(string.ascii_lowercase))
            
            # Add one character from each selected category
            if use_uppercase.get():
                password.append(random.choice(string.ascii_uppercase))
            if use_numbers.get():
                password.append(random.choice(string.digits))
            if use_symbols.get():
                password.append(random.choice(string.punctuation))
            
            # Fill the rest randomly
            remaining_length = length - len(password)
            password.extend(random.choice(chars) for _ in range(remaining_length))
            
            # Shuffle the password
            random.shuffle(password)
            password_var.set(''.join(password))

        def copy_password():
            if password_var.get():
                pyperclip.copy(password_var.get())
                messagebox.showinfo("Success", "Password copied to clipboard!")

        generate_btn = ctk.CTkButton(
            buttons_frame,
            text="Generate",
            command=generate_password,
            **Theme.get_button_style("primary")
        )
        generate_btn.pack(side="left", padx=5)

        copy_btn = ctk.CTkButton(
            buttons_frame,
            text="Copy",
            command=copy_password,
            **Theme.get_button_style("secondary")
        )
        copy_btn.pack(side="left", padx=5)

    def setup_password_manager(self, parent):
        # Title
        title_label = ctk.CTkLabel(
            parent,
            text="Stored Passwords",
            font=Theme.FONTS["title"],
            text_color="#000000"  # Black text
        )
        title_label.pack(pady=20)

        # Search frame
        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)

        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search passwords...",
            **Theme.get_entry_style()
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        def search():
            search_term = search_entry.get()
            self.display_passwords(passwords_frame, search_term)

        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            command=search,
            **Theme.get_button_style("secondary")
        )
        search_btn.pack(side="right")

        # Buttons frame for Add and Manage
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=10)

        add_btn = ctk.CTkButton(
            buttons_frame,
            text="Add New Password",
            command=lambda: self.show_add_password_dialog(),
            **Theme.get_button_style("primary")
        )
        add_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        manage_btn = ctk.CTkButton(
            buttons_frame,
            text="Manage Passwords",
            command=lambda: self.show_manage_passwords_dialog(),
            **Theme.get_button_style("secondary")
        )
        manage_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # Add Change Admin Password button
        change_admin_btn = ctk.CTkButton(
            parent,
            text="Change Admin Password",
            command=self.show_change_admin_password_dialog,
            **Theme.get_button_style("danger")
        )
        change_admin_btn.pack(padx=20, pady=(0, 10), fill="x")

        # Passwords list frame with scrollbar
        passwords_container = ctk.CTkFrame(parent, fg_color="transparent")
        passwords_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Create canvas and scrollbar
        canvas = tk.Canvas(passwords_container, bg=Theme.COLORS["background"], highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(passwords_container, command=canvas.yview)
        passwords_frame = ctk.CTkFrame(canvas, fg_color="transparent")

        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas_frame = canvas.create_window((0, 0), window=passwords_frame, anchor="nw")

        # Update scroll region when frame size changes
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        passwords_frame.bind("<Configure>", configure_scroll_region)

        # Update canvas width when container size changes
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        canvas.bind("<Configure>", configure_canvas_width)

        # Display passwords
        self.display_passwords(passwords_frame)

    def display_passwords(self, container, search_term=""):
        # Clear existing passwords
        for widget in container.winfo_children():
            widget.destroy()

        # Get passwords from database
        passwords = (self.db_manager.search_passwords(search_term) 
                    if search_term else self.db_manager.get_all_passwords())

        if not passwords:
            no_passwords_label = ctk.CTkLabel(
                container,
                text="No passwords found",
                font=Theme.FONTS["main"],
                text_color="#000000"
            )
            no_passwords_label.pack(pady=20)
            return

        for pwd in passwords:
            pwd_id, name, title, username, encrypted_password, description, created_at = pwd
            try:
                password = self.encryption_manager.decrypt(encrypted_password)
            except Exception:
                password = '[Decryption failed]'

            # Password card with rounded corners and shadow effect
            card = ctk.CTkFrame(
                container,
                fg_color="white",
                corner_radius=10,
                border_width=1,
                border_color="#E0E0E0"
            )
            card.pack(fill="x", padx=10, pady=5)

            # Name and timestamp in header
            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=(10, 5))

            name_label = ctk.CTkLabel(
                header_frame,
                text=f"Name: {name}",
                font=("Helvetica", 12, "bold"),
                text_color="#000000"
            )
            name_label.pack(side="left")

            date_label = ctk.CTkLabel(
                header_frame,
                text=created_at,
                font=("Helvetica", 10),
                text_color="#666666"
            )
            date_label.pack(side="right")

            # Separator line
            separator = ctk.CTkFrame(card, height=1, fg_color="#E0E0E0")
            separator.pack(fill="x", padx=15, pady=5)

            # Title and username
            details_frame = ctk.CTkFrame(card, fg_color="transparent")
            details_frame.pack(fill="x", padx=15, pady=5)

            title_label = ctk.CTkLabel(
                details_frame,
                text=f"Title: {title}",
                font=("Helvetica", 11),
                text_color="#000000"
            )
            title_label.pack(side="left")

            username_label = ctk.CTkLabel(
                details_frame,
                text=f"Username: {username}",
                font=("Helvetica", 11),
                text_color="#000000"
            )
            username_label.pack(side="right")

            # Password field with monospace font
            password_frame = ctk.CTkFrame(card, fg_color="transparent")
            password_frame.pack(fill="x", padx=15, pady=5)

            password_var = tk.StringVar(value="•" * len(password))
            password_label = ctk.CTkLabel(
                password_frame,
                textvariable=password_var,
                font=("Courier", 12),  # Monospace font for better password display
                text_color="#000000",
                anchor="w"
            )
            password_label.pack(side="left", padx=(0, 10))

            # Buttons frame
            buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
            buttons_frame.pack(fill="x", padx=15, pady=(5, 10))

            def toggle_password(pwd=password, pwd_var=password_var):
                current = pwd_var.get()
                pwd_var.set(pwd if current.startswith("•") else "•" * len(pwd))

            def copy_password(pwd=password):
                pyperclip.copy(pwd)
                
                # Show temporary success message
                success_label = ctk.CTkLabel(
                    card,
                    text="✓ Password copied!",
                    font=("Helvetica", 10),
                    text_color="#00AA00"
                )
                success_label.pack(pady=5)
                card.after(2000, success_label.destroy)  # Remove after 2 seconds

            def copy_username(uname=username):
                pyperclip.copy(uname)
                
                # Show temporary success message
                success_label = ctk.CTkLabel(
                    card,
                    text="✓ Username copied!",
                    font=("Helvetica", 10),
                    text_color="#00AA00"
                )
                success_label.pack(pady=5)
                card.after(2000, success_label.destroy)  # Remove after 2 seconds

            def delete_password(pwd_id=pwd_id):
                if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this password?"):
                    self.db_manager.delete_password(pwd_id)
                    self.display_passwords(container)

            # Button styles
            button_style = {
                "corner_radius": 6,
                "height": 28,
                "font": ("Helvetica", 10)
            }

            show_btn = ctk.CTkButton(
                buttons_frame,
                text="Show/Hide",
                command=toggle_password,
                width=90,
                fg_color="#000000",
                hover_color="#333333",
                **button_style
            )
            show_btn.pack(side="left", padx=2)

            copy_pwd_btn = ctk.CTkButton(
                buttons_frame,
                text="Copy Pass",
                command=copy_password,
                width=90,
                fg_color="#000000",
                hover_color="#333333",
                **button_style
            )
            copy_pwd_btn.pack(side="left", padx=2)

            copy_user_btn = ctk.CTkButton(
                buttons_frame,
                text="Copy User",
                command=copy_username,
                width=90,
                fg_color="#000000",
                hover_color="#333333",
                **button_style
            )
            copy_user_btn.pack(side="left", padx=2)

            delete_btn = ctk.CTkButton(
                buttons_frame,
                text="Delete",
                command=delete_password,
                width=90,
                fg_color="#FF0000",
                hover_color="#CC0000",
                **button_style
            )
            delete_btn.pack(side="right", padx=2)

            # Description if exists
            if description:
                desc_frame = ctk.CTkFrame(card, fg_color="transparent")
                desc_frame.pack(fill="x", padx=15, pady=(0, 10))
                
                desc_label = ctk.CTkLabel(
                    desc_frame,
                    text=f"Description: {description}",
                    font=("Helvetica", 10),
                    text_color="#666666",
                    wraplength=350  # Wrap long descriptions
                )
                desc_label.pack(anchor="w")

    def show_change_admin_password_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Change Admin Password")
        dialog.geometry("400x300")
        dialog.configure(fg_color="#000000")  # Black background
        
        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 300) // 2
        dialog.geometry(f"400x300+{x}+{y}")

        # Title
        title_label = ctk.CTkLabel(
            dialog,
            text="Change Admin Password",
            font=Theme.FONTS["title"],
            text_color="#FFFFFF"  # White text
        )
        title_label.pack(pady=20)

        # Form frame
        form_frame = ctk.CTkFrame(dialog, **Theme.get_frame_style("card"))
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Current password
        current_password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Current Password",
            show="•",
            **Theme.get_entry_style()
        )
        current_password_entry.pack(padx=20, pady=10, fill="x")

        # New password
        new_password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="New Password",
            show="•",
            **Theme.get_entry_style()
        )
        new_password_entry.pack(padx=20, pady=10, fill="x")

        # Confirm new password
        confirm_password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Confirm New Password",
            show="•",
            **Theme.get_entry_style()
        )
        confirm_password_entry.pack(padx=20, pady=10, fill="x")

        def change_password():
            current = current_password_entry.get()
            new = new_password_entry.get()
            confirm = confirm_password_entry.get()

            if not all([current, new, confirm]):
                messagebox.showerror("Error", "Please fill in all fields!")
                return

            if new != confirm:
                messagebox.showerror("Error", "New passwords do not match!")
                return

            if not self.db_manager.verify_user("admin", current):
                messagebox.showerror("Error", "Current password is incorrect!")
                return

            old_encryption_manager = EncryptionManager(current)
            new_encryption_manager = EncryptionManager(new)

            try:
                with sqlite3.connect(self.db_manager.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, encrypted_password FROM passwords')
                    stored_passwords = cursor.fetchall()

                    # Start transaction
                    conn.execute('BEGIN')
                    for pwd_id, encrypted_password in stored_passwords:
                        try:
                            decrypted = old_encryption_manager.decrypt(encrypted_password)
                        except Exception:
                            conn.rollback()
                            messagebox.showerror("Error", f"Failed to decrypt password with ID {pwd_id}. Password change aborted.\n\nTry using your previous admin password.")
                            return
                        newly_encrypted = new_encryption_manager.encrypt(decrypted)
                        cursor.execute('UPDATE passwords SET encrypted_password = ? WHERE id = ?',
                                     (newly_encrypted, pwd_id))

                    # Update admin password
                    hashed = bcrypt.hashpw(new.encode(), bcrypt.gensalt())
                    cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?',
                                 (hashed.decode(), "admin"))
                    conn.commit()
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {e}\nPassword change aborted.")
                return

            self.encryption_manager = new_encryption_manager
            messagebox.showinfo("Success", "Admin password changed successfully!")
            dialog.destroy()
            self.show_main_screen()

        # Save button
        save_btn = ctk.CTkButton(
            form_frame,
            text="Change Password",
            command=change_password,
            **Theme.get_button_style("primary")
        )
        save_btn.pack(padx=20, pady=20)

    def show_add_password_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New Password")
        dialog.geometry("400x600")
        dialog.configure(fg_color="#000000")  # Black background
        
        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 600) // 2
        dialog.geometry(f"400x600+{x}+{y}")

        # Title
        title_label = ctk.CTkLabel(
            dialog,
            text="Add New Password",
            font=Theme.FONTS["title"],
            text_color="#FFFFFF"  # White text
        )
        title_label.pack(pady=20)

        # Form frame
        form_frame = ctk.CTkFrame(dialog, **Theme.get_frame_style("card"))
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Name entry
        name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Name (e.g., Personal Gmail)",
            **Theme.get_entry_style()
        )
        name_entry.pack(padx=20, pady=10, fill="x")

        # Title entry
        title_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Title (e.g., Email)",
            **Theme.get_entry_style()
        )
        title_entry.pack(padx=20, pady=10, fill="x")

        # Username entry
        username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Username",
            **Theme.get_entry_style()
        )
        username_entry.pack(padx=20, pady=10, fill="x")

        # Password entry
        password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Password",
            show="•",
            **Theme.get_entry_style()
        )
        password_entry.pack(padx=20, pady=10, fill="x")

        # Description entry
        description_entry = ctk.CTkTextbox(
            form_frame,
            height=100,
            **Theme.get_entry_style()
        )
        description_entry.pack(padx=20, pady=10, fill="x")

        def save_password():
            name = name_entry.get().strip()
            title = title_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get()
            description = description_entry.get("1.0", "end-1c").strip()

            if not all([name, title, username, password]):
                messagebox.showerror("Error", "Please fill in all required fields!")
                return

            encrypted_password = self.encryption_manager.encrypt(password)
            self.db_manager.add_password(name, title, username, encrypted_password, description)
            dialog.destroy()
            # Refresh password list
            self.show_main_screen()

        # Save button
        save_btn = ctk.CTkButton(
            form_frame,
            text="Save Password",
            command=save_password,
            **Theme.get_button_style("primary")
        )
        save_btn.pack(padx=20, pady=20)

    def show_manage_passwords_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Manage Passwords")
        dialog.geometry("600x700")
        dialog.configure(fg_color="#000000")  # Black background
        
        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        x = self.root.winfo_x() + (self.root.winfo_width() - 600) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 700) // 2
        dialog.geometry(f"600x700+{x}+{y}")

        # Title
        title_label = ctk.CTkLabel(
            dialog,
            text="Manage Passwords",
            font=Theme.FONTS["title"],
            text_color="#FFFFFF"  # White text
        )
        title_label.pack(pady=20)

        # Search frame
        search_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)

        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search passwords...",
            **Theme.get_entry_style()
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Main container for passwords
        main_container = ctk.CTkFrame(dialog, **Theme.get_frame_style("card"))
        main_container.pack(padx=20, pady=10, fill="both", expand=True)

        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_container, bg="#FFFFFF", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(main_container, command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="transparent")

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width())

        def display_passwords(search_term=""):
            # Clear existing passwords
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            # Get passwords from database
            passwords = (self.db_manager.search_passwords(search_term) 
                        if search_term else self.db_manager.get_all_passwords())

            if not passwords:
                no_passwords_label = ctk.CTkLabel(
                    scrollable_frame,
                    text="No passwords found",
                    font=Theme.FONTS["main"],
                    text_color="#000000"
                )
                no_passwords_label.pack(pady=20)
                return

            for pwd in passwords:
                pwd_id, name, title, username, encrypted_password, description, created_at = pwd
                try:
                    password = self.encryption_manager.decrypt(encrypted_password)
                except Exception:
                    password = '[Decryption failed]'

                # Password card
                card = ctk.CTkFrame(scrollable_frame, **Theme.get_frame_style("card"))
                card.pack(fill="x", padx=10, pady=5)

                # Name and title
                header_frame = ctk.CTkFrame(card, fg_color="transparent")
                header_frame.pack(fill="x", padx=10, pady=5)

                name_label = ctk.CTkLabel(
                    header_frame,
                    text=f"Name: {name}",
                    font=Theme.FONTS["main"],
                    text_color="#000000"
                )
                name_label.pack(side="left")

                title_label = ctk.CTkLabel(
                    header_frame,
                    text=f"Title: {title}",
                    font=Theme.FONTS["main"],
                    text_color="#000000"
                )
                title_label.pack(side="right")

                # Username and password
                details_frame = ctk.CTkFrame(card, fg_color="transparent")
                details_frame.pack(fill="x", padx=10, pady=5)

                username_label = ctk.CTkLabel(
                    details_frame,
                    text=f"Username: {username}",
                    font=Theme.FONTS["main"],
                    text_color="#000000"
                )
                username_label.pack(side="left")

                password_var = tk.StringVar(value="•" * len(password))
                password_label = ctk.CTkLabel(
                    details_frame,
                    textvariable=password_var,
                    font=Theme.FONTS["main"],
                    text_color="#000000"
                )
                password_label.pack(side="right")

                # Description if exists
                if description:
                    desc_label = ctk.CTkLabel(
                        card,
                        text=f"Description: {description}",
                        font=("Helvetica", 10),
                        text_color="#000000"
                    )
                    desc_label.pack(padx=10, pady=5)

                # Buttons frame
                buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
                buttons_frame.pack(fill="x", padx=10, pady=5)

                def toggle_password(pwd=password, pwd_var=password_var):
                    current = pwd_var.get()
                    pwd_var.set(pwd if current.startswith("•") else "•" * len(pwd))

                def copy_password(pwd=password):
                    pyperclip.copy(pwd)
                    messagebox.showinfo("Success", "Password copied to clipboard!")

                def copy_username(uname=username):
                    pyperclip.copy(uname)
                    messagebox.showinfo("Success", "Username copied to clipboard!")

                def delete_password(pwd_id=pwd_id):
                    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this password?"):
                        self.db_manager.delete_password(pwd_id)
                        display_passwords(search_entry.get())
                        self.show_main_screen()  # Refresh main screen

                show_btn = ctk.CTkButton(
                    buttons_frame,
                    text="Show/Hide",
                    command=toggle_password,
                    width=100,
                    **Theme.get_button_style("secondary")
                )
                show_btn.pack(side="left", padx=2)

                copy_pwd_btn = ctk.CTkButton(
                    buttons_frame,
                    text="Copy Pass",
                    command=copy_password,
                    width=100,
                    **Theme.get_button_style("secondary")
                )
                copy_pwd_btn.pack(side="left", padx=2)

                copy_user_btn = ctk.CTkButton(
                    buttons_frame,
                    text="Copy User",
                    command=copy_username,
                    width=100,
                    **Theme.get_button_style("secondary")
                )
                copy_user_btn.pack(side="left", padx=2)

                delete_btn = ctk.CTkButton(
                    buttons_frame,
                    text="Delete",
                    command=delete_password,
                    width=100,
                    **Theme.get_button_style("danger")
                )
                delete_btn.pack(side="right", padx=2)

        def on_search():
            display_passwords(search_entry.get())

        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            command=on_search,
            **Theme.get_button_style("secondary")
        )
        search_btn.pack(side="right")

        # Configure scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", configure_scroll_region)

        def configure_canvas_width(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        canvas.bind("<Configure>", configure_canvas_width)

        # Initial display
        display_passwords()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PasswordManagerGUI()
    app.run() 
