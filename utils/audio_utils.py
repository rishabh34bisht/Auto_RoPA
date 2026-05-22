# utils/audio_utils.py
import subprocess
import os
import tempfile
from pydub import AudioSegment

def extract_audio(video_path: str, output_audio_path: str) -> bool:
    """
    Extracts audio from a video file using FFmpeg.
    """
    command = [
        "ffmpeg", "-y", "-i", video_path, 
        "-vn", "-acodec", "libmp3lame", 
        "-q:a", "2", output_audio_path
    ]
    
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        return True
    except FileNotFoundError:
        raise Exception("FFmpeg is not installed or not in the system PATH.")
    except Exception as e:
        raise Exception(f"Error extracting audio: {str(e)}")


def chunk_audio_file(audio_path: str, chunk_length_ms: int = 600000) -> list:
    """
    Checks file size. If > 24MB, chunks it into smaller MP3 files.
    chunk_length_ms defaults to 10 minutes (600,000 ms).
    Returns a list of file paths.
    """
    MAX_SIZE = 24 * 1024 * 1024 # 24 MB safety limit
    file_size = os.path.getsize(audio_path)
    
    if file_size <= MAX_SIZE:
        return [audio_path] # No chunking needed

    # Load audio and chunk it
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        
        # Create a temp file for the chunk
        fd, temp_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        
        # Export as MP3 (ensures 10 mins is well under 25MB)
        chunk.export(temp_path, format="mp3", bitrate="128k")
        chunks.append(temp_path)
        
    return chunks