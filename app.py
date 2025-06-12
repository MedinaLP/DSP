import io
import numpy as np
import streamlit as st
import librosa, librosa.display
import matplotlib.pyplot as plt
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment

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

# ---------- FILE UPLOAD ----------
MAX_MB = 50  # Recommended file size limit for good performance
MAX_BYTES = MAX_MB * 1024 * 1024

file = st.file_uploader(f"📤 Upload a .wav file (≤ {MAX_MB} MB recommended)", type=["wav"])

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

def reduce_noise(y, sr):
    noise_clip = y[: int(0.5 * sr)]
    return nr.reduce_noise(y=y, sr=sr, y_noise=noise_clip, prop_decrease=1.0)

def wav_to_mp3(y, sr):
    y16 = np.int16(y / np.max(np.abs(y)) * 32767)
    wav_buf = io.BytesIO()
    sf.write(wav_buf, y16, sr, format="WAV", subtype="PCM_16")  # Explicit format
    wav_buf.seek(0)
    
    segment = AudioSegment.from_file(wav_buf, format="wav")
    mp3_buf = io.BytesIO()
    segment.export(mp3_buf, format="mp3", bitrate="192k")
    mp3_buf.seek(0)
    return mp3_buf


# ---------- PROCESSING ----------
if file is not None:
    if file.size > MAX_BYTES:
        size_mb = file.size / (1024 * 1024)
        st.warning(f"⚠️ File is {size_mb:.2f} MB. > {MAX_MB} MB may slow processing or timeout.")

    st.audio(file, format="audio/wav", start_time=0)

    if st.button("🚀 Clean up audio"):
        with st.spinner("Processing…"):
            y, sr = librosa.load(file, sr=None, mono=True)
            y_clean = reduce_noise(y, sr)

            st.subheader("🔍 Spectrogram Comparison")
            col1, col2 = st.columns(2)
            with col1:
                plot_spectrogram(y, sr, "Original (Noisy)")
            with col2:
                plot_spectrogram(y_clean, sr, "Cleaned")

            mp3_buf = wav_to_mp3(y_clean, sr)
            st.success("✅ Done! Download your cleaned audio below ⬇️")
            st.download_button("💾 Download MP3",
                               data=mp3_buf,
                               file_name="audio_cleaned.mp3",
                               mime="audio/mpeg")
