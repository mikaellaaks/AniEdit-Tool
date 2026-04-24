import ffmpeg
import re
import threading
from typing import Union, Optional, Callable
from src.playlist_utils import fetch_master_playlist, parse_variant_playlists, select_valid_media_playlist, hms_to_seconds
from src.api import get_episode_link
import imageio_ffmpeg


def _configure_ffmpeg_kwargs(start_time: Optional[str], end_time: Optional[str], remove_watermark: bool, remove_subtitles: bool) -> tuple[dict, dict]:
    """Configure the input and output keyword arguments for ffmpeg."""
    input_kwargs = {
        'allowed_extensions': 'ALL'
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
    remove_subtitles: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    cancel_event: Optional[threading.Event] = None
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
            
        ffmpeg_cmd = imageio_ffmpeg.get_ffmpeg_exe()

        process = (
            ffmpeg.output(video, stream.audio, output_path, **output_kwargs)
            .run_async(pipe_stderr=True, pipe_stdout=True, overwrite_output=True, cmd=ffmpeg_cmd)
        )
        
        duration_sec = 0.0
        # If clipping using `-t`, the exact output duration is predetermined
        if 't' in output_kwargs:
            duration_sec = float(output_kwargs['t'])
            
        time_regex = re.compile(r"time=(?P<time>\d+:\d+:\d+\.\d+)")
        duration_regex = re.compile(r"Duration: (?P<duration>\d+:\d+:\d+\.\d+)")
        
        # Read the stderr stream line by line to calculate progress
        while True:
            if cancel_event and cancel_event.is_set():
                process.terminate()
                process.wait()
                return False
                
            line = process.stderr.readline()
            if not line:
                break
                
            line_str = line.decode('utf-8', errors='ignore')
            
            # If we don't know the duration, try to parse it from the initial stream metadata (Duration: 00:24:00.00)
            if duration_sec == 0.0:
                dur_match = duration_regex.search(line_str)
                if dur_match:
                    dur_str = dur_match.group("duration")
                    h, m, s = dur_str.split(':')
                    duration_sec = float(h) * 3600 + float(m) * 60 + float(s)
                    
            if progress_callback and duration_sec > 0:
                time_match = time_regex.search(line_str)
                if time_match:
                    t_str = time_match.group("time")
                    h, m, s = t_str.split(':')
                    current_sec = float(h) * 3600 + float(m) * 60 + float(s)
                    
                    # Compute percentage
                    percent = min(100, int((current_sec / duration_sec) * 100))
                    progress_callback(percent, 100)
                    
        process.wait()
        
        if process.returncode != 0:
            print(f"Error downloading video. Return code: {process.returncode}")
            return False
            
        if progress_callback:
            progress_callback(100, 100)
            
        print(f"Download complete: {output_path}")
        return True

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error downloading video: {e}")
        return False


def download_pipeline(
    page_url: str, 
    output_path: str, 
    start_time: str | None = None, 
    end_time: str | None = None, 
    video_type: str = "softsub", 
    server: str = "Server 1",
    progress_callback: Optional[Callable[[int, int], None]] = None,
    cancel_event: Optional[threading.Event] = None
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
            remove_subtitles=True,
            progress_callback=progress_callback,
            cancel_event=cancel_event
        )
    return False
