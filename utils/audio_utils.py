# utils/audio_utils.py
import subprocess
import os
import tempfile
import glob

def extract_audio(video_path: str, output_audio_path: str) -> bool:
    """Extracts audio from a video file using FFmpeg."""
    command = [
        "ffmpeg", "-y", "-i", video_path, 
        "-vn", "-acodec", "libmp3lame", 
        "-q:a", "2", output_audio_path
    ]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return True
    except Exception as e:
        raise Exception(f"Error extracting audio: {str(e)}")


def chunk_audio_file(audio_path: str, segment_time_seconds: int = 600) -> list:
    """
    Forces audio to be sliced into 10-minute chunks using FFmpeg, 
    bypassing OpenAI's silent truncation limit.
    """
    temp_dir = tempfile.mkdtemp()
    output_pattern = os.path.join(temp_dir, "chunk_%03d.mp3")
    
    # We re-encode to a clean 64k mp3. This guarantees precise 10-min cuts, 
    # perfect voice quality for AI, and incredibly small file sizes.
    command = [
        "ffmpeg", "-y", "-i", audio_path,
        "-f", "segment",
        "-segment_time", str(segment_time_seconds),
        "-c:a", "libmp3lame",
        "-b:a", "64k",
        output_pattern
    ]
    
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Fetch all the dynamically generated chunks
    chunks = sorted(glob.glob(os.path.join(temp_dir, "chunk_*.mp3")))
    
    if not chunks:
        return [audio_path] # Fallback in case of an error
        
    return chunks
