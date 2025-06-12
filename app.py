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

# ---------- FUNCTIONS ----------
def plot_waveform(y, sr, title):
    time = np.linspace(0, len(y) / sr, num=len(y))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time, y=y, mode='lines', name='Amplitude'))
    fig.update_layout(title=title, xaxis_title='Time (s)', yaxis_title='Amplitude')
    st.plotly_chart(fig, use_container_width=True)

def plot_spectrogram(y, sr, title):
    S = np.abs(librosa.stft(y))
    S_db = librosa.amplitude_to_db(S, ref=np.max)
    times = librosa.frames_to_time(np.arange(S_db.shape[1]), sr=sr)
    freqs = librosa.fft_frequencies(sr=sr)
    fig = go.Figure(data=go.Heatmap(z=S_db, x=times, y=freqs, colorscale='Viridis'))
    fig.update_layout(title=title, xaxis_title='Time (s)', yaxis_title='Frequency (Hz)')
    st.plotly_chart(fig, use_container_width=True)

def reduce_noise(y, sr):
    noise_clip = y[:int(0.5 * sr)]
    return nr.reduce_noise(y=y, sr=sr, y_noise=noise_clip, prop_decrease=1.0)

def wav_to_mp3(y, sr):
    y16 = np.int16(y / np.max(np.abs(y)) * 32767)
    wav_buf = io.BytesIO()
    sf.write(wav_buf, y16, sr, format='WAV', subtype='PCM_16')
    wav_buf.seek(0)

    segment = AudioSegment.from_file(wav_buf, format="wav")
    mp3_buf = io.BytesIO()
    segment.export(mp3_buf, format="mp3", bitrate="192k")
    mp3_buf.seek(0)
    return mp3_buf

def convert_mp3_to_wav(mp3_file):
    audio = AudioSegment.from_file(mp3_file, format="mp3")
    wav_buf = io.BytesIO()
    audio.export(wav_buf, format="wav")
    wav_buf.seek(0)
    return wav_buf

# ---------- TAB INDEX HANDLING ----------
if "tab_index" not in st.session_state:
    st.session_state["tab_index"] = 0

# ---------- TABS ----------
tabs = st.tabs(["🏠 Home", "🎧 AudiVive", "ℹ️ About"])

# ---------- HOME TAB ----------
with tabs[0]:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f0fffe;
        }
        .center-btn {
            text-align: center;
            margin-top: 2em;
        }
        .center-btn button {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
        }
        </style>
        <h1 style='text-align: center; color: #3853ff;'>၊၊||၊</h1>
        <h1 style='text-align: center; color: #1a1a1a;'>AudioVive</h1>
        <h3 style='text-align: center; font-weight: 400; color: #333;'>Where old audio finds new life</h3>
        <p style='text-align: center;'>Clean and enhance noisy or distorted recordings from the past using modern audio technology.</p>
        <div class='center-btn'>
            <a href="#🎧-audivive"><button>🚀 Get Started with AudiVive!</button></a>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- AUDIOVIVE TAB ----------
with tabs[1]:
    st.header("၊၊||၊ AudioVive")
    
    MAX_MB = 50
    MAX_BYTES = MAX_MB * 1024 * 1024
    file = st.file_uploader(f"Upload an audio file (≤ {MAX_MB} MB recommended)", type=["wav", "mp3"])

    if file is not None:
        if file.size > MAX_BYTES:
            size_mb = file.size / (1024 * 1024)
            st.warning(f"⚠️ File is {size_mb:.2f} MB. > {MAX_MB} MB may slow processing or timeout.")

        file_bytes = file.read()

        # Convert mp3 to wav if needed
        if file.type == "audio/mpeg":
            st.info("Converting MP3 to WAV for processing...")
            file = convert_mp3_to_wav(io.BytesIO(file_bytes))
        else:
            file = io.BytesIO(file_bytes)

        st.audio(file, format="audio/wav", start_time=0)

        y, sr = librosa.load(file, sr=None, mono=True)
        st.session_state["raw_audio"] = y
        st.session_state["sr"] = sr

        if st.button("🚀 Clean up audio"):
            with st.spinner("Processing…"):
                y_clean = reduce_noise(y, sr)
                st.session_state["cleaned_audio"] = y_clean

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

        mp3_buf = wav_to_mp3(y_clean, sr)
        st.success("Done! Download your cleaned audio below ⬇️")
        st.download_button("💾 Download MP3", data=mp3_buf, file_name="audio_cleaned.mp3", mime="audio/mpeg")

# ---------- ABOUT TAB ----------
with tabs[2]:
    st.markdown("""
    ### 📌 About AudiVive
    Modern digital tools can help restore and improve the quality of older audio recordings, which often have background noise and difficulty in interpretation. This process revitalizes history by restoring sounds with clearer sound, ensuring it remains remembered for future generations.

    ### 👥 About the Creators
    **Medina**  
    **Maestre**  
    **Malsi**  
    **Zablan**

    We're a team passionate about technology and preservation — blending digital innovation with heritage restoration.
    """)
