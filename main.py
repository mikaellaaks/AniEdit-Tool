"""
Entry point for AniEdit-Tool as a pure Python program (no web server).
"""
import subprocess
import atexit
import os
import sys
from tui.tui import AniEdit

# Start the local API server process
api_cwd = os.path.join(os.path.dirname(__file__), "local_api")
api_process = subprocess.Popen(
    [sys.executable, "app.py"], 
    cwd=api_cwd,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

def cleanup_api():
    if api_process.poll() is None:
        api_process.terminate()

atexit.register(cleanup_api)

def main():
    app = AniEdit()
    app.run()

if __name__ == "__main__":
    main()
