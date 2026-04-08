# AniEdit-Tool

AniEdit-Tool is a standalone Python program with a Textual User Interface (TUI) for downloading and clipping anime episodes directly from AnimeKAI. It provides a terminal interface to trim episodes before downloading them.

## Features

- **Textual User Interface (TUI):** A clean terminal-based UI.
- **Download from AnimeKAI:** Paste an episode URL.
- **Clipping:** Specify optional `MM:SS` or `HH:MM:SS` start and end times to trim your clip before downloading.

## Prerequisites

- **Python 3.10+**
- **FFmpeg:** Must be installed on your system and accessible in your system `PATH`.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Application:**
   ```bash
   python main.py
   ```

## Usage

1. Launch the program via `main.py`.
2. In the terminal UI, insert the **AnimeKAI URL** for the episode.
3. Enter the desired **output filename** (without the extension).
4. *(Optional)* Enter the **Start Time** and **End Time**. It supports `MM:SS` (e.g., `01:30`) and `HH:MM:SS` formats.
5. Press **Start Download**. A progress bar will appear indicating the process is running.
6. Once completed, a file explorer window will appear to let you choose exactly where to save the downloaded `.mp4` file.

## Credits

Thanks to [walterwhite-69](https://github.com/walterwhite-69) for providing the backend scraping engine, [AnimeKAI REST API](https://github.com/walterwhite-69/AnimeKAI-API).

## License

MIT License

*Educational use only*
