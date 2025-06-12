import io
import numpy as np
import streamlit as st
import librosa, librosa.display
import matplotlib.pyplot as plt
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment
import plotly.graph_objects as go

st.set_page_config(page_title="AudioVive", page_icon="🎵", layout="centered")

# ---------- STYLING & HEADER ----------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0fffe;
    }
    </style>
    <h1 style='text-align: center; color: #3853ff;'>၊၊||၊</h1>
    <h1 style='text-align: center; color: #1a1a1a;'>AudioVive</h1>
    <h3 style='text-align: center; font-weight: 400; color: #333;'>Where old audio finds new life</h3>
    """,
    unsafe_allow_html=True
)

# ---------- FUNCTIONS ----------

def plot_spectrogram(y, sr, title: str):
    fig, ax = plt.subplots()
    S = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    img = librosa.display.specshow(S, sr=sr, x_axis="time", y_axis="hz", ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    fig.colorbar(img, ax=ax, format="%+2.0f dB")
    st.pyplot(fig)

def plot_waveform(y, sr, title: str):
    fig, ax = plt.subplots()
    times = np.arange(len(y)) / sr
    ax.plot(times, y, color='blue')
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)

def reduce_noise(y, sr):
    noise_clip = y[: int(0.5 * sr)]
    return nr.reduce_noise(y=y, sr=sr, y_noise=noise_clip, prop_decrease=1.0)

def wav_to_mp3(y, sr):
    y16 = np.int16(y / np.max(np.abs(y)) * 32767)
    wav_buf = io.BytesIO()
    sf.write(wav_buf, y16, sr, format="WAV", subtype="PCM_16")
    wav_buf.seek(0)

    segment = AudioSegment.from_file(wav_buf, format="wav")
    mp3_buf = io.BytesIO()
    segment.export(mp3_buf, format="mp3", bitrate="192k")
    mp3_buf.seek(0)
    return mp3_buf

# ---------- MAIN APP ----------

MAX_MB = 50
MAX_BYTES = MAX_MB * 1024 * 1024

uploaded_file = st.file_uploader(
    f"Upload a .wav or .mp3 file (≤ {MAX_MB} MB recommended)",
    type=["wav", "mp3"]
)

if uploaded_file:
    if uploaded_file.size > MAX_BYTES:
        st.warning(f"⚠️ File is {uploaded_file.size / (1024 * 1024):.2f} MB. > {MAX_MB} MB may slow processing or timeout.")

    if "raw_audio" not in st.session_state:
        file_ext = uploaded_file.name.split('.')[-1].lower()

        if file_ext == "mp3":
            audio = AudioSegment.from_file(uploaded_file, format="mp3")
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            y, sr = librosa.load(wav_io, sr=None, mono=True)
        else:  # wav
            y, sr = librosa.load(uploaded_file, sr=None, mono=True)

        st.session_state["raw_audio"] = y
        st.session_state["sr"] = sr
        st.session_state["cleaned_audio"] = reduce_noise(y, sr)

    st.audio(uploaded_file, format="audio/wav" if uploaded_file.name.endswith(".wav") else "audio/mp3")
    
# ---------- Visualization Toggle ----------
if "raw_audio" in st.session_state and "cleaned_audio" in st.session_state:
    y = st.session_state["raw_audio"]
    y_clean = st.session_state["cleaned_audio"]
    sr = st.session_state["sr"]

    st.subheader("🔍 Audio Visualization")
    view_option = st.radio("Choose audio visualization:", ["Waveform", "Spectrogram"], horizontal=True)

    col1, col2 = st.columns(2)
    with col1:
        if view_option == "Waveform":
            plot_waveform(y, sr, "Original (Noisy)")
        else:
            plot_spectrogram(y, sr, "Original (Noisy)")

    with col2:
        if view_option == "Waveform":
            plot_waveform(y_clean, sr, "Cleaned")
        else:
            plot_spectrogram(y_clean, sr, "Cleaned")

    # ---------- Cleaned Audio Download ----------
    st.markdown("---")
    st.subheader("🎧 Download Cleaned Audio")
    mp3_buf = wav_to_mp3(y_clean, sr)
    st.download_button("💾 Download MP3", data=mp3_buf, file_name="audio_cleaned.mp3", mime="audio/mpeg")
