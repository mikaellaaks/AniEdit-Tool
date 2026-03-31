import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlsplit

load_dotenv()
API_KEY = os.getenv("API_KEY")


def parse_episode_url(url: str):

    split_url = urlsplit(url)

    path = split_url.path.split("/")[-1]
    query = split_url.query.split("=")[-1]

    episode_id = f"{path}$episode${query}"
    
    return episode_id


def get_episode_link(url: str, video_type="sub", server="vidcloud"):

    episode_id = parse_episode_url(url)

    url = f"https://anime-streaming.p.rapidapi.com/watch/{episode_id}"

    querystring = {"type":video_type,"server":server}

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "anime-streaming.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params=querystring)
    raw_data = response.json()
    
    episode_link = parse_episode_link(raw_data)

    return episode_link

def parse_episode_link(raw_data):

    url = raw_data['sources'].pop()['url']
    return url