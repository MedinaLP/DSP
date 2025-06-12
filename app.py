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

def apply_notch_filter(y, sr, freq=60.0, quality=30.0):
    b, a = iirnotch(freq, quality, sr)
    return lfilter(b, a, y)

def reduce_noise(y, sr):
    y_filtered = apply_notch_filter(y, sr)
    noise_clip = y_filtered[:int(0.5 * sr)]
    return nr.reduce_noise(y=y_filtered, sr=sr, y_noise=noise_clip, prop_decrease=1.0)

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

def compute_snr(clean, noise):
    signal_power = np.mean(clean ** 2)
    noise_power = np.mean(noise ** 2)
    snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
    return snr

# ---------- TAB INDEX HANDLING ----------
if "tab_index" not in st.session_state:
    st.session_state["tab_index"] = 0

# ---------- TABS ----------
tabs = st.tabs(["🏠 Home", "🎧 AudioVive", "📊 Visualization", "📈 Evaluation", "ℹ️ About"])

# ---------- HOME TAB ----------
with tabs[0]:
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
        <p style='text-align: center;'>
            Clean and enhance noisy or distorted recordings from the past using modern audio technology.
        </p>
        <p style='text-align: center;'>
            AudioVive lets you <strong>hear the past more clearly</strong>. Using intelligent filtering and enhancement tools, 
            it removes background noise and improves overall audio quality. Whether it’s a cherished voice message or a piece of history, 
            AudioVive helps you <strong>relive meaningful moments</strong> and preserve them for the future.
        </p>
        """,
        unsafe_allow_html=True
    )

    if st.button("🎶 Get Started with AudioVive!", use_container_width=True):
        st.markdown("---")
        st.markdown("### ❓ How AudioVive Works")
    
        st.markdown("""
        1. **Upload your audio file**  
           Select an audio file in either **WAV** or **MP3** format. Whether it's a vintage voice recording or an old music clip, AudioVive can process it.
    
        2. **Restore the sound with a single click**  
           With just one click, AudioVive removes background hum, hiss, and noise using advanced filtering technology to enhance clarity.
    
        3. **Visualize the transformation**  
           Instantly see the difference between the original and cleaned audio through interactive **Waveform** and **Spectrogram** visualizations.
    
        4. **Download the enhanced audio**  
           Once processed, download your cleaned file as an **MP3**—ready to archive, share, or enjoy.
    
        """)
        st.success("✨ You're all set! Click the '🎧 AudioVive' tab above to begin restoring your audio.")

# ---------- AUDIOVIVE TAB ----------
with tabs[1]:
    st.header("🎧 Restore your Old Audios with AudioVive!")
    MAX_MB = 50
    MAX_BYTES = MAX_MB * 1024 * 1024
    file = st.file_uploader(f"Upload an audio file (Recommended file size should not exceed {MAX_MB} MB)", type=["wav", "mp3"])

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

        if st.button("🚀 Clean up audio", use_container_width=True):
            with st.spinner("Processing…"):
                y_clean = reduce_noise(y, sr)
                st.session_state["cleaned_audio"] = y_clean

                mp3_buf = wav_to_mp3(st.session_state.get("cleaned_audio", y), sr)
                st.success("Done! Download your cleaned audio below ⬇️")
                st.download_button("💾 Download MP3", use_container_width=True, data=mp3_buf, file_name="audio_cleaned.mp3", mime="audio/mpeg")

# ---------- VISUALIZATION TAB ----------
with tabs[2]:
    
    if "raw_audio" in st.session_state and "cleaned_audio" in st.session_state:
        y = st.session_state["raw_audio"]
        y_clean = st.session_state["cleaned_audio"]
        sr = st.session_state["sr"]

        st.header("🔍 Audio Visualization")
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

        noise_est = y - y_clean
        snr_before = compute_snr(y, noise_est)
        snr_after = compute_snr(y_clean, noise_est)

        st.subheader("📊 Signal-to-Noise Ratio (SNR)")
        st.markdown(f"**SNR Before Cleaning:** {snr_before:.2f} dB")
        st.markdown(f"**SNR After Cleaning:** {snr_after:.2f} dB")
    else:
        st.info("Please upload and process an audio file in the '🎧 AudioVive' tab first.")

# ---------- EVALUATION TAB ----------
with tabs[3]:
    st.header("📈 Audio Evaluation with MATLAB Standards")
    if "raw_audio" in st.session_state and "cleaned_audio" in st.session_state:
        y = st.session_state["raw_audio"]
        y_clean = st.session_state["cleaned_audio"]
        sr = st.session_state["sr"]

        noise_est = y - y_clean
        snr_before = compute_snr(y, noise_est)
        snr_after = compute_snr(y_clean, noise_est)

        st.markdown(f"**SNR Before Cleaning:** {snr_before:.2f} dB")
        st.markdown(f"**SNR After Cleaning:** {snr_after:.2f} dB")

        if snr_after > snr_before:
            st.success("✅ The noise reduction process was effective.")
        else:
            st.warning("⚠️ No significant improvement in SNR. Consider adjusting parameters.")

        st.markdown("""
        ### 🔬 Evaluation Pipeline Summary:
        - Audio sample is tested and visualized using waveform and spectrogram.
        - FFT is used for frequency analysis.
        - Notch filter is applied at 60 Hz for targeted noise removal.
        - Spectral subtraction is done frame by frame based on a noise profile.
        - Signal-to-Noise Ratio (SNR) is calculated to quantify effectiveness.
        """)
    else:
        st.info("Please upload and process an audio file first to evaluate.")
        
# ---------- ABOUT TAB ----------
with tabs[4]:
    st.markdown("""
    ### 📌 About AudioVive
    AudioVive is a modern tool designed to restore and enhance the quality of old audio recordings—particularly those affected by background noise, distortion, or low fidelity. By using advanced filtering and noise reduction techniques, our app helps revive historical sounds—from archival speech to vintage music—making them clearer, crisper, and more accessible for future generations.

    This project demonstrates how digital platforms like Streamlit and GitHub can be used to:
    
     ✅ Remove persistent hum, hiss, or other noise using intelligent filtering  
     ✅ Improve the clarity and quality of archived audio  
     ✅ Reconstruct and preserve valuable auditory content using open-source tools

    ### 👥 About the Creators
    We're a team passionate about technology, preservation, and digital innovation, each contributing unique strengths to make AudioVive a reality:

    **Medina** – Software Development & Streamlit Integration  
    Responsible for implementing the app architecture and audio processing pipeline using Python and Streamlit.

    **Maestre** – Data Processing & Audio Enhancement  
    In charge of handling audio inputs, refining cleaning techniques, and ensuring smooth audio transformations.

    **Malsi** – Documentation & Research  
    Oversees user flow, writes clear and concise documentation, and contributes to research supporting the app's purpose.

    **Zablan** – UI Design & Project Coordination  
    Designs the user interface, ensures a visually intuitive experience, and coordinates overall project development and goals.
    """)
