# app.py
import streamlit as st
import os
import tempfile
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

from utils.audio_utils import extract_audio
from utils.transcription import transcribe_audio
from utils.mom_generator import generate_mom
from utils.ropa_generator import generate_ropa
from utils.export_utils import create_docx, create_excel
from utils.audio_utils import extract_audio, chunk_audio_file

# Load Environment Variables
# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
api_key = st.secrets["OPENAI_API_KEY"]

# App config
st.set_page_config(page_title="AI Privacy Meeting Assistant", page_icon="🔒", layout="wide")

# Initialize Session State
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'mom_content' not in st.session_state:
    st.session_state.mom_content = None
if 'ropa_data' not in st.session_state:
    st.session_state.ropa_data = None
if 'token_usage' not in st.session_state:
    st.session_state.token_usage = {"mom": None, "ropa": None}

st.title("🔒 AI Privacy Meeting Assistant")
st.markdown("Upload meeting recordings to automatically transcribe, generate Minutes of Meeting (MoM), and extract Data Privacy Records (RoPA).")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    if not api_key:
        st.error("OpenAI API Key not found in .env file.")
        st.stop()
    else:
        st.success("API Key Loaded.")
    
    client = OpenAI(api_key=api_key)
    
    st.divider()
    st.subheader("RoPA Settings")
    ropa_mode = st.radio("Extraction Mode", ["Auto Detect", "User Input"])
    
    manual_config = None
    if ropa_mode == "User Input":
        num_acts = st.number_input("Number of Processing Activities", min_value=1, max_value=10, value=1)
        titles = st.text_input("Activity Titles (Comma separated)", placeholder="e.g., HR Onboarding, Payroll")
        if titles:
            manual_config = {
                "num_activities": num_acts,
                "titles": [t.strip() for t in titles.split(",")]
            }

# --- STEP 1: UPLOAD ---
uploaded_file = st.file_uploader("Upload Audio or Video", type=['mp3', 'wav', 'm4a', 'mp4', 'mov', 'mkv'])

if uploaded_file is not None and st.button("🚀 Process Media"):
    st.session_state.transcript = None 
    
    with st.status("Processing Pipeline started...", expanded=True) as status:
        try:
            # 1. File Handling & Audio Extraction
            file_ext = uploaded_file.name.split('.')[-1].lower()
            is_video = file_ext in ['mp4', 'mov', 'mkv']
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                media_path = tmp_file.name

            target_audio_path = media_path
            
            if is_video:
                st.write("🎞️ Video detected. Extracting audio...")
                target_audio_path = media_path.replace(f".{file_ext}", ".mp3")
                extract_audio(media_path, target_audio_path)
            
            # 2. Transcription with Chunking
            st.write("🎙️ Checking file size and preparing Whisper chunks...")
            audio_chunks = chunk_audio_file(target_audio_path)
            
            if len(audio_chunks) > 1:
                st.write(f"📂 Audio exceeds 25MB. Seamlessly split into {len(audio_chunks)} chunks.")
                
            st.write("📝 Transcribing audio...")
            transcript = transcribe_audio(client, audio_chunks)
            st.session_state.transcript = transcript
            
            # 3. Generate MoM
            st.write("📊 Generating Minutes of Meeting...")
            mom, mom_usage = generate_mom(client, transcript)
            st.session_state.mom_content = mom
            st.session_state.token_usage['mom'] = mom_usage
            
            # 4. Generate RoPA
            st.write("🔒 Extracting RoPA data...")
            ropa, ropa_usage = generate_ropa(client, transcript, ropa_mode, manual_config)
            st.session_state.ropa_data = ropa
            st.session_state.token_usage['ropa'] = ropa_usage

            status.update(label="Processing Complete!", state="complete", expanded=False)

        except Exception as e:
            status.update(label="Error occurred", state="error", expanded=True)
            st.error(f"Pipeline failed: {str(e)}")
            
        finally:
            # Cleanup temp files
            import shutil
            
            if os.path.exists(media_path): 
                os.remove(media_path)
            if is_video and os.path.exists(target_audio_path): 
                os.remove(target_audio_path)
                
            # Safely delete the directory containing all the audio chunks
            if 'audio_chunks' in locals() and len(audio_chunks) > 0:
                chunk_dir = os.path.dirname(audio_chunks[0])
                if os.path.exists(chunk_dir) and ("tmp" in chunk_dir.lower() or "temp" in chunk_dir.lower()):
                    shutil.rmtree(chunk_dir, ignore_errors=True)

# --- RESULTS DISPLAY ---
if st.session_state.transcript:
    tab1, tab2, tab3 = st.tabs(["📄 Transcript", "📝 Minutes of Meeting", "📊 RoPA Export"])
    
    # Transcript Tab
    with tab1:
        st.text_area("Full Transcription", st.session_state.transcript, height=300)
        st.download_button("⬇️ Download TXT", data=st.session_state.transcript, file_name="transcript.txt", mime="text/plain")
        
    # MoM Tab
    with tab2:
        st.info("You can edit the MoM below before downloading.")
        edited_mom = st.text_area("Minutes of Meeting", st.session_state.mom_content, height=400)
        st.session_state.mom_content = edited_mom # Update state
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("⬇️ Download MoM (TXT)", data=edited_mom, file_name="MoM.txt", mime="text/plain")
        with col2:
            docx_file = create_docx(edited_mom)
            st.download_button("⬇️ Download MoM (DOCX)", data=docx_file, file_name="MoM.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
        if st.session_state.token_usage['mom']:
            st.caption(f"Tokens used for MoM: {st.session_state.token_usage['mom']['total_tokens']}")

    # RoPA Tab
    with tab3:
        st.info("You can edit the RoPA table directly in the grid below before exporting to Excel.")
        
        # Convert to Pandas for editing
        df = pd.DataFrame(st.session_state.ropa_data)
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        # Update session state with edited data
        st.session_state.ropa_data = edited_df.to_dict('records')
        
        excel_file = create_excel(st.session_state.ropa_data)
        st.download_button("⬇️ Download RoPA (Excel)", data=excel_file, file_name="ROPA.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        if st.session_state.token_usage['ropa']:
            st.caption(f"Tokens used for RoPA extraction: {st.session_state.token_usage['ropa']['total_tokens']}")
