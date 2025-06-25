from typing import Dict, Any

class Theme:
    # Color scheme
    COLORS = {
        "primary": "#000000",  # Pure black
        "secondary": "#000000",  # Pure black
        "accent": "#000000",  # Pure black
        "background": "#F6B17A",  # Soft orange
        "text": "#000000",  # Black
        "error": "#000000",  # Pure black
        "success": "#000000",  # Pure black
        "warning": "#000000",  # Pure black
        "sparkle": "#FFFFFF",  # White sparkles
        "sparkle_alt": "#FFD700",  # Gold sparkles
    }

    # Font configurations
    FONTS = {
        "main": ("Helvetica", 12, "bold"),
        "title": ("Helvetica", 16, "bold"),
        "button": ("Helvetica", 11, "bold"),
        "input": ("Helvetica", 11, "bold"),
    }

    # Button styles
    BUTTON_STYLES = {
        "primary": {
            "fg_color": "#000000",  # Pure black
            "hover_color": "#333333",  # Slightly lighter black
            "text_color": "#FFFFFF",  # Pure white
            "font": FONTS["button"],
            "corner_radius": 8,
        },
        "secondary": {
            "fg_color": "#000000",  # Pure black
            "hover_color": "#333333",  # Slightly lighter black
            "text_color": "#FFFFFF",  # Pure white
            "font": FONTS["button"],
            "corner_radius": 8,
        },
        "danger": {
            "fg_color": "#000000",  # Pure black
            "hover_color": "#333333",  # Slightly lighter black
            "text_color": "#FFFFFF",  # Pure white
            "font": FONTS["button"],
            "corner_radius": 8,
        }
    }

    # Entry styles
    ENTRY_STYLES = {
        "normal": {
            "fg_color": "white",
            "border_color": "#000000",  # Pure black
            "text_color": "#000000",  # Black text
            "font": FONTS["input"],
            "corner_radius": 8,
        }
    }

    # Frame styles
    FRAME_STYLES = {
        "main": {
            "fg_color": COLORS["background"],
            "corner_radius": 10,
        },
        "card": {
            "fg_color": "white",
            "corner_radius": 10,
        }
    }

    # Animation configurations
    ANIMATIONS = {
        "button_click": {
            "duration": 150,  # milliseconds
            "scale_factor": 0.95,
        },
        "success_checkmark": {
            "duration": 500,  # milliseconds
            "color": "#000000",  # Pure black
        },
        "error_shake": {
            "duration": 300,  # milliseconds
            "distance": 10,  # pixels
        }
    }

    @classmethod
    def get_button_style(cls, style_name: str) -> Dict[str, Any]:
        return cls.BUTTON_STYLES.get(style_name, cls.BUTTON_STYLES["primary"])

    @classmethod
    def get_entry_style(cls, style_name: str = "normal") -> Dict[str, Any]:
        return cls.ENTRY_STYLES.get(style_name, cls.ENTRY_STYLES["normal"])

    @classmethod
    def get_frame_style(cls, style_name: str) -> Dict[str, Any]:
        return cls.FRAME_STYLES.get(style_name, cls.FRAME_STYLES["main"]) 