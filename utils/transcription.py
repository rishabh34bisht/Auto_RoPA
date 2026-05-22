# utils/transcription.py
from openai import OpenAI

def transcribe_audio(client: OpenAI, audio_file_paths: list) -> str:
    """
    Transcribes a list of audio chunks using OpenAI Whisper.
    Uses context prompting to ensure no accuracy drop across boundaries.
    """
    full_transcript = ""
    previous_transcript_end = ""
    
    for path in audio_file_paths:
        with open(path, "rb") as audio_file:
            # Pass the last 200 chars of the previous segment to maintain context
            prompt = previous_transcript_end[-200:] if previous_transcript_end else ""
            
            response = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="text",
                prompt=prompt,
                language="en",    
                temperature=0.0  
            )
            
            # Response is a string when response_format="text"
            transcript_text = response
            full_transcript += transcript_text + " "
            
            # Update previous transcript end for the next iteration
            previous_transcript_end = transcript_text
            
    return full_transcript.strip()