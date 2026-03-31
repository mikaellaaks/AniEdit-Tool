import ffmpeg
from typing import Union, Optional
from src.playlist_utils import fetch_master_playlist, parse_variant_playlists, select_valid_media_playlist, hms_to_seconds

def download_m3u8(m3u8_url: Union[str, tuple], output_path: str, start_time: Optional[str] = None, end_time: Optional[str] = None):
    # Support receiving a tuple of (url, referer) or just the url
    if isinstance(m3u8_url, tuple):
        url, referer = m3u8_url
    else:
        url = m3u8_url
        referer = "https://megacloud.blog/"
        
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    headers = {"User-Agent": user_agent, "Referer": referer}
    
    # Parse and select the best playlist stream
    master_content = fetch_master_playlist(url, headers)
    variant_lines = parse_variant_playlists(master_content)
    media_playlist_url = select_valid_media_playlist(variant_lines, url, headers) if variant_lines else url

    # Configure ffmpeg commands for trimming and downloading
    ffmpeg_input_kwargs = {}
    ffmpeg_output_kwargs = {}

    if start_time or end_time:
        # HLS stream fast-seeking (-ss on input) jumps to the nearest segment boundary,
        # which often cuts off the first few seconds. To fix this, we back up the input
        # seek by 15 seconds to grab the preceding segment, then trim accurately on the output.
        start_seconds = hms_to_seconds(start_time) if start_time else 0
        seek_offset = 15
        
        if start_seconds > seek_offset:
            input_ss = start_seconds - seek_offset
            output_ss = seek_offset
        else:
            input_ss = 0
            output_ss = start_seconds
            
        ffmpeg_input_kwargs['ss'] = str(input_ss)
        
        if output_ss > 0:
            ffmpeg_output_kwargs['ss'] = str(output_ss)

        if end_time:
            end_seconds = hms_to_seconds(end_time)
            duration = end_seconds - start_seconds
            if duration > 0:
                ffmpeg_output_kwargs['t'] = str(duration)
    else:
        # If fully downloading, copy the stream directly for speed
        ffmpeg_output_kwargs = {'c': 'copy', 'bsf:a': 'aac_adtstoasc'}

    try:
        (
            ffmpeg
            .input(
                media_playlist_url,
                headers=f"User-Agent: {user_agent}\r\nReferer: {referer}\r\n",
                **ffmpeg_input_kwargs
            )
            .output(output_path, **ffmpeg_output_kwargs)
            .run(overwrite_output=True)
        )
        print(f"Download complete: {output_path}")

    except ffmpeg.Error as e:
        print(f"Error downloading video: {e}")
