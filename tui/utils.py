import os
import re
import json

SETTINGS_FILE = "settings.json"

def remove_file(path):
    """Remove a file from the given path."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
    return

def load_settings():
    """Load settings from the local JSON file."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(settings):
    """Save settings to the local JSON file."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Failed to save settings: {e}")

def validate_input(url, output_file, start_time=None, end_time=None):
    """Validate the input parameters"""
    if not url:
        return False, "URL is required!"
        
    if not output_file:
        return False, "Output filename is required!"
    
    if not (url.startswith("http://") or url.startswith("https://")):
        return False, "Invalid URL! Must start with http:// or https://"

    # Time validation: allow empty or mm:ss (e.g., 01:30)
    time_pattern = re.compile(r"^(?:[0-5]?\d:[0-5]\d)?$")
    if start_time and not time_pattern.match(start_time):
        return False, "Invalid Start Time format! Use mm:ss"
    if end_time and not time_pattern.match(end_time):
        return False, "Invalid End Time format! Use mm:ss"

    return True, ""

