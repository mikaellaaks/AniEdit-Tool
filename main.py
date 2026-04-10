"""
Entry point for AniEdit-Tool as a pure Python program (no web server).
"""
import subprocess
import atexit
import os
import sys
from tui.tui import AniEdit
from animekai_api.app import app as flask_app
import threading
import logging
import os
import sys


cli = sys.modules.get('flask.cli')
if cli:
    cli.show_server_banner = lambda *args: None

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Start the local API server process
def run_api():
    # Run flask app
    flask_app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

api_thread = threading.Thread(target=run_api, daemon=True)
api_thread.start()

def main():
    app = AniEdit()
    app.run()

if __name__ == "__main__":
    main()
