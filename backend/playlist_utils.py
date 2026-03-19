import requests
import re
from urllib.parse import urljoin
from typing import List, Tuple, Dict

def fetch_master_playlist(m3u8_url: str, headers: Dict[str, str]) -> str:
    """Download the master M3U8 playlist."""
    resp = requests.get(m3u8_url, headers=headers)
    resp.raise_for_status()
    return resp.text

def parse_variant_playlists(master_content: str) -> List[Tuple[int, str]]:
    """Parse the master playlist for variant streams, returning a list of (bandwidth, url)."""
    variant_lines = []
    master_lines = master_content.splitlines()
    
    for i, line in enumerate(master_lines):
        if line.startswith("#EXT-X-STREAM-INF:") and i + 1 < len(master_lines):
            bandwidth = 0
            match = re.search(r'BANDWIDTH=(\d+)', line)
            if match:
                bandwidth = int(match.group(1))
            
            url_line = master_lines[i + 1].strip()
            variant_lines.append((bandwidth, url_line))
            
    return variant_lines

def select_valid_media_playlist(variant_lines: List[Tuple[int, str]], m3u8_url: str, headers: Dict[str, str]) -> str:
    """Find the highest bandwidth playlist that contains actual video segments (.ts)."""
    print("Checking candidate media playlists for valid video segments...")
    
    # Sort variants by bandwidth in descending order
    for bw, url_line in sorted(variant_lines, key=lambda x: -x[0]):
        candidate_url = urljoin(m3u8_url, url_line)
        
        try:
            pl_resp = requests.get(candidate_url, headers=headers)
            pl_resp.raise_for_status()
            
            # Extract content segments, ignoring comments
            segment_lines = [seg.strip() for seg in pl_resp.text.splitlines() if seg and not seg.startswith('#')]
            segment_types = set(seg.split('.')[-1].lower() for seg in segment_lines if '.' in seg)
            
            print(f"Candidate: {candidate_url}\n  Bandwidth: {bw}\n  Segment types: {segment_types}")
            
            # Check for valid .ts segments and ensure it's not a dummy playlist of .jpgs
            has_ts = any(seg.lower().endswith('.ts') for seg in segment_lines)
            has_jpg = any(seg.lower().endswith('.jpg') for seg in segment_lines)
            
            if has_ts and not has_jpg:
                print(f"Selected media playlist: {candidate_url}")
                return candidate_url
                
        except Exception as e:
            print(f"Error checking playlist {candidate_url}: {e}")
            continue

    print("No valid video playlist found. All candidates were non-video or invalid.")
    raise Exception("No valid video playlist (.ts segments) found in master.m3u8.")

def hms_to_seconds(hms: str) -> int:
    """Convert a time string (HH:MM:SS) to total seconds."""
    h, m, s = [int(x) for x in hms.split(":")]
    return h * 3600 + m * 60 + s

