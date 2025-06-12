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

# ---------- SETTINGS ----------
MAX_MB = 50
MAX_BYTES = MAX_MB * 1024 * 1024

uploaded_file = st.file_uploader(
    f"Upload a .wav or .mp3 file (\u2264 {MAX_MB} MB recommended)",
    type=["wav", "mp3"]
)

# ---------- FUNCTIONS ----------
def reduce_noise(y, sr):
    noise_clip = y[: int(0.5 * sr)]
    return nr.reduce_noise(y=y, sr=sr, y_noise=noise_clip, prop_decrease=1.0)

def wav_to_mp3(y, sr):
    y16 = np.int16(y / np.max(np.abs(y)) * 32767)
    wav_buf = io.BytesIO()
    sf.write(wav_buf, y16, sr, subtype="PCM_16")
    wav_buf.seek(0)

    segment = AudioSegment.from_file(wav_buf, format="wav")
    mp3_buf = io.BytesIO()
    segment.export(mp3_buf, format="mp3", bitrate="192k")
    mp3_buf.seek(0)
    return mp3_buf

def plot_waveform(y, sr, title="Waveform"):
    times = np.arange(len(y)) / sr
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=y, mode='lines', name='Amplitude'))
    fig.update_layout(title=title, xaxis_title='Time (s)', yaxis_title='Amplitude')
    st.plotly_chart(fig, use_container_width=True)

def plot_spectrogram_interactive(y, sr, title="Spectrogram"):
    S = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    fig = go.Figure(data=go.Heatmap(z=S, colorscale='Viridis'))
    fig.update_layout(title=title, xaxis_title='Time', yaxis_title='Frequency (Hz)')
    st.plotly_chart(fig, use_container_width=True)

# ---------- MAIN LOGIC ----------
if uploaded_file:
    if uploaded_file.size > MAX_BYTES:
        st.warning(f"\u26a0\ufe0f File is {uploaded_file.size / (1024 * 1024):.2f} MB. > {MAX_MB} MB may slow processing or timeout.")

    file_ext = uploaded_file.name.split('.')[-1].lower()

    if file_ext == "mp3":
        audio = AudioSegment.from_file(uploaded_file, format="mp3")
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        y, sr = librosa.load(wav_io, sr=None, mono=True)
    else:
        y, sr = librosa.load(uploaded_file, sr=None, mono=True)

    st.audio(uploaded_file, format="audio/wav" if file_ext == "wav" else "audio/mp3")

    if st.button("\ud83d\ude80 Clean up audio"):
        with st.spinner("Processing..."):
            y_clean = reduce_noise(y, sr)

            st.subheader("\ud83d\udd0d Visual Comparison")
            view_option = st.radio("Choose visualization:", ["Waveform", "Spectrogram"], horizontal=True)
            col1, col2 = st.columns(2)

            with col1:
                if view_option == "Waveform":
                    plot_waveform(y, sr, "Original (Noisy)")
                else:
                    plot_spectrogram_interactive(y, sr, "Original (Noisy)")

            with col2:
                if view_option == "Waveform":
                    plot_waveform(y_clean, sr, "Cleaned")
                else:
                    plot_spectrogram_interactive(y_clean, sr, "Cleaned")

            mp3_buf = wav_to_mp3(y_clean, sr)
            st.success("💾 Download your cleaned audio below \u2b07\ufe0f")
            st.download_button("\ud83d\udce5 Download MP3", data=mp3_buf, file_name="audio_cleaned.mp3", mime="audio/mpeg")
