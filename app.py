import streamlit as st

st.set_page_config(page_title="AudioVive", page_icon="🎵", layout="centered")

# Add custom background color (sky blue)
st.markdown(
    """
    <style>
    body {
        background-color: #dbefff; /* Pale sky blue */
    }
    .main {
        background-color: #dbefff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Centered header and subheader
st.markdown(
    """
    <h1 style='text-align: center; color: #1a1a1a;'>🎵 AudioVive</h1>
    <h3 style='text-align: center; font-weight: 400; color: #333;'>Where old audio finds new life</h3>
    """,
    unsafe_allow_html=True
)
