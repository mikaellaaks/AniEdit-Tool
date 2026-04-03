"""
Entry point for AniEdit-Tool as a pure Python program (no web server).
"""
from src.api import get_episode_link
from src.downloader import download_m3u8
from tui.tui import AniEdit

# Example usage function (replace with CLI or GUI later)
def main():
    app = AniEdit()
    app.run()

if __name__ == "__main__":
    main()
