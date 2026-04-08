import ffmpeg
from typing import Union, Optional
from src.playlist_utils import fetch_master_playlist, parse_variant_playlists, select_valid_media_playlist, hms_to_seconds
from src.api import get_episode_link


def _configure_ffmpeg_kwargs(start_time: Optional[str], end_time: Optional[str], remove_watermark: bool, remove_subtitles: bool) -> tuple[dict, dict]:
    """Configure the input and output keyword arguments for ffmpeg."""
    input_kwargs = {
        'allowed_extensions': 'ALL',
        'allowed_segment_extensions': 'ALL',
        'extension_picky': 0
    }
    output_kwargs = {}

    if remove_subtitles:
        output_kwargs['sn'] = None

    if start_time or end_time:
        start_seconds = hms_to_seconds(start_time) if start_time else 0
        seek_offset = 15
        
        if start_seconds > seek_offset:
            input_ss = start_seconds - seek_offset
            output_ss = seek_offset
        else:
            input_ss = 0
            output_ss = start_seconds
            
        input_kwargs['ss'] = str(input_ss)
        
        if output_ss > 0:
            output_kwargs['ss'] = str(output_ss)

        if end_time:
            end_seconds = hms_to_seconds(end_time)
            duration = end_seconds - start_seconds
            if duration > 0:
                output_kwargs['t'] = str(duration)
                
        output_kwargs['bsf:a'] = 'aac_adtstoasc'
        if not remove_watermark:
            output_kwargs['c'] = 'copy'
    else:
        output_kwargs['bsf:a'] = 'aac_adtstoasc'
        if remove_watermark:
            output_kwargs['preset'] = 'fast'
        else:
            output_kwargs['c'] = 'copy'

    return input_kwargs, output_kwargs


def download_m3u8(
    m3u8_url: Union[str, tuple], 
    output_path: str, 
    start_time: Optional[str] = None, 
    end_time: Optional[str] = None, 
    remove_watermark: bool = True, 
    remove_subtitles: bool = True
) -> bool:
    """Download and process an M3U8 stream using ffmpeg."""
    url, referer = m3u8_url if isinstance(m3u8_url, tuple) else (m3u8_url, "https://megacloud.blog/")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    headers = {"User-Agent": user_agent, "Referer": referer}
    
    print(f"[DEBUG] Downloading: {url} -> {output_path} ({start_time} - {end_time})")

    master_content = fetch_master_playlist(url, headers)
    variant_lines = parse_variant_playlists(master_content)
    media_playlist_url = select_valid_media_playlist(variant_lines, url, headers) if variant_lines else url

    input_kwargs, output_kwargs = _configure_ffmpeg_kwargs(start_time, end_time, remove_watermark, remove_subtitles)

    try:
        stream = ffmpeg.input(
            media_playlist_url,
            headers=f"User-Agent: {user_agent}\r\nReferer: {referer}\r\n",
            **input_kwargs
        )
        
        video = stream.video
        if remove_watermark:
            video = video.filter('delogo', x='1760', y='10', w='150', h='50')
            
        (
            ffmpeg.output(video, stream.audio, output_path, **output_kwargs)
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        print(f"Download complete: {output_path}")
        return True

    except ffmpeg.Error as e:
        print(f"Error downloading video: {e}")
        if e.stderr:
            print(f"[ffmpeg stderr]\n{e.stderr.decode(errors='ignore')}")
        return False


def download_pipeline(
    page_url: str, 
    output_path: str, 
    start_time: str | None = None, 
    end_time: str | None = None, 
    video_type: str = "softsub", 
    server: str = "Server 1"
) -> bool:
    """Extract m3u8 link from an Animekai URL and download the video."""
    m3u8_url = get_episode_link(page_url, video_type=video_type, server=server)
    
    if m3u8_url:
        return download_m3u8(
            m3u8_url, 
            output_path, 
            start_time, 
            end_time, 
            remove_watermark=True, 
            remove_subtitles=True
        )
    return False
