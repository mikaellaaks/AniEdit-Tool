# AniEdit-Tool

AniEdit-Tool is a standalone Python program with a Textual User Interface (TUI) for downloading and clipping anime episodes directly from AniWatch. It provides a terminal interface to trim episodes before downloading them.

## Features

- **Textual User Interface (TUI):** A clean terminal-based UI.
- **Download from AniWatch:** Paste an episode URL.
- **Clipping:** Specify optional `MM:SS` or `HH:MM:SS` start and end times to trim your clip before downloading.

## Prerequisites

- **Python 3.10+**
- **FFmpeg:** Must be installed on your system and accessible in your system `PATH`.
- **RapidAPI Key:** You need an API key for the `anime-streaming` API to fetch sources.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your RapidAPI key:
   ```env
   API_KEY=your_rapidapi_key_here
   ```

3. **Run the Application:**
   ```bash
   python main.py
   ```

## Usage

1. Launch the program via `main.py`.
2. In the terminal UI, insert the **Aniwatch URL** for the episode.
3. Enter the desired **output filename** (without the extension).
4. *(Optional)* Enter the **Start Time** and **End Time**. It supports `MM:SS` (e.g., `01:30`) and `HH:MM:SS` formats.
5. Press **Start Download**. A progress bar will appear indicating the process is running.
6. Once completed, a native file explorer window will appear to let you choose exactly where to save the downloaded `.mp4` file.

## License

MIT License
