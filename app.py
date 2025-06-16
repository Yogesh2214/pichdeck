import streamlit as st
from openai import OpenAI
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
from datetime import datetime
import wave
import pyaudio
import tempfile
import threading
import queue
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set page config
st.set_page_config(
    page_title="Pitch Call Summarizer",
    page_icon="🎯",
    layout="wide"
)

# Create recordings directory if it doesn't exist
if not os.path.exists("recordings"):
    os.makedirs("recordings")

# Initialize session state
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = []
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'mic_available' not in st.session_state:
    st.session_state.mic_available = False
if 'recording_filename' not in st.session_state:
    st.session_state.recording_filename = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'recording_start_time' not in st.session_state:
    st.session_state.recording_start_time = None
if 'recording_duration' not in st.session_state:
    st.session_state.recording_duration = 0

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

def check_microphone():
    """Check if microphone is available"""
    try:
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                st.session_state.mic_available = True
                p.terminate()
                return True
        p.terminate()
        return False
    except Exception as e:
        st.error(f"Error checking microphone: {str(e)}")
        return False

def record_audio():
    """Record system audio"""
    if not st.session_state.mic_available:
        st.error("No audio input device detected. Please connect a microphone and refresh the page.")
        return

    try:
        st.session_state.audio_data = []
        st.session_state.recording = True
        st.session_state.recording_start_time = time.time()
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Open stream
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        st.write("🎤 Recording... Click 'Stop Recording' when finished.")
        
        # Record audio
        while st.session_state.recording:
            data = stream.read(CHUNK)
            st.session_state.audio_data.append(data)
            
            # Update recording duration
            st.session_state.recording_duration = time.time() - st.session_state.recording_start_time
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save the recording
        if st.session_state.audio_data:
            filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            filepath = os.path.join("recordings", filename)
            wf = wave.open(filepath, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(st.session_state.audio_data))
            wf.close()
            st.session_state.recording_filename = filename
            st.success(f"Recording saved as {filename}")
            return filename
        return None
    except Exception as e:
        st.error(f"Error during recording: {str(e)}")
        st.session_state.recording = False
        return None

def stop_recording():
    """Stop recording"""
    st.session_state.recording = False

def generate_summary(text):
    """Generate summary using ChatGPT"""
    prompt = f"""Please analyze this pitch call transcript and extract the following key points:
    1. Project Information
    2. Target Market
    3. Market Needs/Problems
    4. Why Invest
    5. Funding Ask
    6. Use Cases
    7. Revenue Model/How they make profit

    Format the response in a clear, structured way.

    Transcript: {text}"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional pitch call analyzer."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

# Main UI
st.title("🎯 Pitch Call Summarizer")

# Check microphone availability
if not st.session_state.mic_available:
    check_microphone()

# Recording Section
st.header("1. Record Call")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Start Recording", disabled=st.session_state.recording):
        record_audio()

with col2:
    if st.button("Stop Recording", disabled=not st.session_state.recording):
        stop_recording()

with col3:
    if st.session_state.recording:
        st.metric("Recording Duration", f"{int(st.session_state.recording_duration)} seconds")

# Show recording status
if st.session_state.recording:
    st.warning("🎤 Recording in progress...")
elif st.session_state.recording_filename:
    st.success(f"✅ Recording saved as: {st.session_state.recording_filename}")

# Transcription Section
st.header("2. Transcription")
transcript = st.text_area("Enter the transcript:", value=st.session_state.transcript, height=200)
if transcript != st.session_state.transcript:
    st.session_state.transcript = transcript

# Summary Section
st.header("3. Generated Summary")
if st.button("Generate Summary"):
    if st.session_state.transcript:
        with st.spinner("Generating summary..."):
            summary = generate_summary(st.session_state.transcript)
            if summary:
                st.session_state.summary = summary
                st.markdown(summary)
    else:
        st.warning("Please enter the transcript first!")

# Export Section
if st.session_state.summary:
    st.header("4. Export")
    export_text = f"""# Pitch Call Summary

## Generated Summary
{st.session_state.summary}

## Full Transcript
{st.session_state.transcript}
"""
    st.download_button(
        label="Download Summary",
        data=export_text,
        file_name="pitch_summary.md",
        mime="text/markdown"
    )

# Instructions
with st.expander("How to use"):
    st.markdown("""
    1. Make sure your system audio is properly configured
    2. Click 'Start Recording' to begin recording the call
    3. Click 'Stop Recording' when finished
    4. Enter the transcript manually
    5. Click 'Generate Summary' to analyze the pitch
    6. Download the final summary
    """) 