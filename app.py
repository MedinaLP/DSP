import streamlit as st

st.set_page_config(page_title="AudioVive", page_icon="🎵", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0fffe;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h1 style='text-align: center; color: #3853ff;'>၊၊||၊</h1>
    <h1 style='text-align: center; color: #1a1a1a;'>AudioVive</h1>
    <h3 style='text-align: center; font-weight: 400; color: #333;'>Where old audio finds new life</h3>
    """,
    unsafe_allow_html=True
)

# Upload .wav file
audio_file = st.file_uploader("Upload your audio file (.wav, max 10MB)", type=["wav"])

# Max file size: 10MB
MAX_SIZE = 10 * 1024 * 1024  # 10 MB in bytes

if audio_file is not None:
    if audio_file.size > MAX_SIZE:
        st.error("⚠️ File too large. Please upload a .wav file under 10MB.")
    else:
        st.success("✅ File uploaded successfully!")
        st.audio(audio_file, format="audio/wav")
