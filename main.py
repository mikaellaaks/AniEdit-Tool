"""
Entry point for AniEdit-Tool as a pure Python program (no web server).
"""
from src.api import get_episode_link
from src.downloader import download_m3u8

# Example usage function (replace with CLI or GUI later)
def main():
    print("AniEdit-Tool (Python version)")
    url = input("Enter AniWatch episode URL: ")
    output_file = input("Enter output file name: ")
    start_time = input("Start time (hh:mm:ss or blank): ") or None
    end_time = input("End time (hh:mm:ss or blank): ") or None

    m3u8_link = get_episode_link(url)
    download_m3u8(m3u8_link, output_file, start_time, end_time)

if __name__ == "__main__":
    main()
