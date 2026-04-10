import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlsplit

load_dotenv()
API_KEY = os.getenv("API_KEY")


def parse_episode_url(url: str):

    split_url = urlsplit(url)
    slug = split_url.path.split("/")[-1]
    
    ep_num = "1"
    if split_url.fragment and split_url.fragment.startswith("ep="):
        ep_num = split_url.fragment.split("=")[-1]
    elif split_url.query and "ep=" in split_url.query:
        ep_num = split_url.query.split("ep=")[-1].split("&")[0]

    return slug, ep_num


def get_episode_link(url: str, video_type="sub", server="Server 1"):

    slug, ep_num = parse_episode_url(url)

    try:
        # 1. Fetch anime info to get ani_id
        anime_resp = requests.get(f"http://127.0.0.1:5000/api/anime/{slug}").json()
        if not anime_resp.get("success"):
            return None
        ani_id = anime_resp.get("ani_id")

        # 2. Fetch episodes to get the token matching this episode number
        episodes_resp = requests.get(f"http://127.0.0.1:5000/api/episodes/{ani_id}").json()
        server_token = None
        
        if episodes_resp.get("success") and "episodes" in episodes_resp:
            for ep in episodes_resp["episodes"]:
                if str(ep.get("number")) == str(ep_num):
                    server_token = ep.get("token")
                    break

        if not server_token:
            return None

        # 3. Fetch servers
        servers_resp = requests.get(f"http://127.0.0.1:5000/api/servers/{server_token}").json()
        link_id = None
        
        if servers_resp.get("success") and "servers" in servers_resp:
            available_servers = servers_resp["servers"].get(video_type, [])
            for srv in available_servers:
                # Matches "Server 1", "Server 2", etc.
                if srv["name"].lower() == server.lower():
                    link_id = srv["link_id"]
                    break
            
            # fallback to first available if requested server wasn't found
            if not link_id and len(available_servers) > 0:
                link_id = available_servers[0]["link_id"]

        # 4. Fetch actual m3u8 source
        if link_id:
            source_resp = requests.get(f"http://127.0.0.1:5000/api/source/{link_id}").json()
            if source_resp.get("success") and "sources" in source_resp:
                return source_resp["sources"][0]["file"]
                
        return None
    except Exception:
        # Return None to fail gracefully on invalid URLs or bad API responses
        return None

def parse_episode_link(raw_data):
    if isinstance(raw_data, str):
        return raw_data
    url = raw_data['sources'].pop()['url']
    return url