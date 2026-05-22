# utils/transcription.py
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def transcribe_audio(client: OpenAI, audio_file_paths: list) -> str:
    """Transcribes a list of audio chunks with UI progress tracking."""
    full_transcript = ""
    previous_transcript_end = ""
    
    total_chunks = len(audio_file_paths)
    
    # Create UI elements for progress tracking
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    for idx, path in enumerate(audio_file_paths):
        progress_text.text(f"🎙️ Transcribing chunk {idx + 1} of {total_chunks}...")
        
        with open(path, "rb") as audio_file:
            # Pass the last 200 chars to maintain context seamlessly across chunks
            prompt = previous_transcript_end[-200:] if previous_transcript_end else ""
            
            response = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe", 
                file=audio_file,
                response_format="text",
                prompt=prompt
            )
            
            transcript_text = response
            full_transcript += transcript_text + " "
            previous_transcript_end = transcript_text
            
        # Update progress bar
        progress_bar.progress((idx + 1) / total_chunks)
        
    progress_text.text("✅ Transcription complete!")
    return full_transcript.strip()
