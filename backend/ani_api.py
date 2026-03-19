import requests
import time

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
    # Make the API request with retries
    max_retries = 3
    json_output = None
    
    for attempt in range(max_retries):
        try:
            result = requests.get(url, headers=headers)
            result.raise_for_status()
            json_output = result.json()
            break
        except requests.RequestException as e:
            print(f"API request failed: {e}. Retrying ({attempt + 1}/{max_retries})...")
            if attempt == max_retries - 1:
                raise e
            time.sleep(2)

    if not json_output or "data" not in json_output or "sources" not in json_output["data"]:
        raise Exception("Invalid or empty API response.")

    # Extract video sources from the API response
    sources = json_output["data"]["sources"]
    if not sources:
        raise Exception("No sources found in API response.")
    
    episode_url = sources[0]["url"]

    # Extract Referer header if provided (needed for ffmpeg download)
    referer = json_output["data"].get("headers", {}).get("Referer", "https://megacloud.blog/")
    
    return episode_url, referer


def get_video_id(url: str):
    split_url = url.split("/")
    video_id = split_url[-1]
    
    return video_id


