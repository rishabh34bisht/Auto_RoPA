# AI Privacy Meeting Assistant

A production-ready Streamlit application that automates your post-meeting workflows. It takes audio/video recordings, transcribes them using OpenAI Whisper, generates Minutes of Meeting (MoM), and extracts structured GDPR/Privacy RoPA (Record of Processing Activities) tables.

## Prerequisites
1. **Python 3.9+**
2. **FFmpeg** installed on your system (Required for extracting audio from video files).
   - **Windows:** `winget install ffmpeg` or download from ffmpeg.org
   - **Mac:** `brew install ffmpeg`
   - **Linux:** `sudo apt install ffmpeg`
3. **OpenAI API Key**

## Installation

1. Clone the repository and navigate into it.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate