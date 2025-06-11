import streamlit as st

st.set_page_config(page_title="AudioVive", page_icon="🎵", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background-color: ##f0fffe;
    }
    </style>
    <div style="text-align: center;">
        <img src="audiovive.png" width="100">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <h1 style='text-align: center; color: #1a1a1a;'>AudioVive</h1>
    <h3 style='text-align: center; font-weight: 400; color: #333;'>Where old audio finds new life</h3>
    """,
    unsafe_allow_html=True
)
