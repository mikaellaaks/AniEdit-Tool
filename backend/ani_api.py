import requests
import re
from urllib.parse import urljoin
import ffmpeg

HOST = "http://192.168.50.233:4000"
URL_BASE = "/api/v2/hianime"

def get_episode_url(episode_id: str, server="hd-2", category: str="sub"):

    # Build the API URL for the episode sources endpoint
    url = f"{HOST}{URL_BASE}/episode/sources?animeEpisodeId={episode_id}&server={server}&category={category}"

    # Set a browser-like User-Agent and accept JSON
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    # Make the API request
    result = requests.get(url, headers=headers)
    result.raise_for_status()
    json_output = result.json()

    # Extract video sources from the API response
    sources = json_output["data"]["sources"]
    if not sources:
        raise Exception("No sources found in API response.")
    
    episode_url = sources[0]["url"]

    # Extract Referer header if provided (needed for ffmpeg download)
    referer = json_output["data"].get("headers", {}).get("Referer", "https://megacloud.blog/")

    return episode_url, referer


def fetch_master_playlist(m3u8_url, headers):
    """
    Download the master M3U8 playlist using the provided headers
    Returns the playlist content as a string
    """

    resp = requests.get(m3u8_url, headers=headers)
    resp.raise_for_status()
    return resp.text


def parse_variant_playlists(master_content):
    """
    Parse the master playlist for all variant stream entries
    Returns a list of (bandwidth, url) tuples for each variant
    """
    
    variant_lines = []
    master_lines = master_content.splitlines()
    for i, line in enumerate(master_lines):
        if line.startswith("#EXT-X-STREAM-INF:"):
            # The next line after EXT-X-STREAM-INF is the playlist URL
            if i+1 < len(master_lines):
                bandwidth = 0
                match = re.search(r'BANDWIDTH=(\d+)', line)
                if match:
                    bandwidth = int(match.group(1))
                url_line = master_lines[i+1].strip()
                variant_lines.append((bandwidth, url_line))
    return variant_lines


def select_valid_media_playlist(variant_lines, m3u8_url, headers):
    """
    For each variant playlist, download and check for valid video segments (.ts, not .jpg).
    Returns the first valid media playlist URL found, or raises an Exception if none are valid.
    """

    print("Checking candidate media playlists for valid video segments...")
    # Try each variant playlist, highest bandwidth first, and pick the first with valid .ts segments
    for bw, url_line in sorted(variant_lines, key=lambda x: -x[0]):
        candidate_url = urljoin(m3u8_url, url_line)
        try:
            # Download the candidate media playlist
            pl_resp = requests.get(candidate_url, headers=headers)
            pl_resp.raise_for_status()
            pl_content = pl_resp.text
            
            # Extract segment lines (ignore comments and empty lines)
            segment_lines = [seg for seg in pl_content.splitlines() if seg and not seg.startswith('#')]
            segment_types = set(seg.strip().split('.')[-1].lower() for seg in segment_lines if '.' in seg)
            print(f"Candidate: {candidate_url}\n  Bandwidth: {bw}\n  Segment types: {segment_types}")
            
            # Only accept if at least one segment ends with .ts and none are .jpg
            if any(seg.strip().lower().endswith('.ts') for seg in segment_lines) and not any(seg.strip().lower().endswith('.jpg') for seg in segment_lines):
                print(f"Selected media playlist: {candidate_url}")
                return candidate_url
            
        except Exception as e:
            print(f"Error checking playlist {candidate_url}: {e}")
            continue

    print("No valid video playlist found. All candidates were non-video or invalid.")
    raise Exception("No valid video playlist (.ts segments) found in master.m3u8.")

def download_m3u8(m3u8_url: str, output_path: str, start_time: str = None, end_time: str = None):
    """
    Download an HLS video stream (M3U8) to a file, handling master playlists and variant selection.
    Accepts either a tuple (url, referer) or just the URL. Selects the best video variant and downloads it using ffmpeg.
    Optionally, specify start_time and end_time as HH:MM:SS strings to trim the output.
    """

    # Accepts a tuple (url, referer)
    if isinstance(m3u8_url, tuple):
        m3u8_url, referer = m3u8_url
    else:
        referer = "https://megacloud.blog/"

    headers = {
        # Set User-Agent and Referer for ffmpeg to bypass 403 errors
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": referer
    }

    master_content = fetch_master_playlist(m3u8_url, headers)
    variant_lines = parse_variant_playlists(master_content)

    # Select the best valid media playlist, or use the original if no variants
    if variant_lines:
        media_playlist_url = select_valid_media_playlist(variant_lines, m3u8_url, headers)
    else:
        media_playlist_url = m3u8_url

    # Calculate duration if both start and end are given
    ffmpeg_input_kwargs = {}
    ffmpeg_output_kwargs = {'c': 'copy', 'bsf:a': 'aac_adtstoasc'}
    if start_time:
        ffmpeg_input_kwargs['ss'] = start_time
    if start_time and end_time:
        # Convert HH:MM:SS to seconds
        def hms_to_seconds(hms):
            h, m, s = [int(x) for x in hms.split(":")]
            return h * 3600 + m * 60 + s
        duration = hms_to_seconds(end_time) - hms_to_seconds(start_time)
        ffmpeg_output_kwargs['t'] = str(duration)
    elif end_time:
        ffmpeg_output_kwargs['to'] = end_time

    # Run ffmpeg to download the video using ffmpeg-python
    try:
        (
            ffmpeg
            .input(
                media_playlist_url,
                headers=f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36\r\nReferer: {referer}\r\n",
                **ffmpeg_input_kwargs
            )
            .output(
                output_path,
                **ffmpeg_output_kwargs
            )
            .run(overwrite_output=True)
        )
        print(f"Download complete: {output_path}")
    except ffmpeg.Error as e:
        print("Error downloading video:", e)

def main():
    
    # Example usage: download from 2:00 to 4:00 (2 minutes)
    video_url, _ = get_episode_url("your-lie-in-april-31?ep=926")
    output_path = "output.mp4"
    download_m3u8(video_url, output_path, start_time="00:02:00", end_time="00:04:00")


if __name__ == "__main__":
    main()