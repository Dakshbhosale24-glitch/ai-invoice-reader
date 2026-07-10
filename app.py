import streamlit as st

st.set_page_config(
    page_title="AI Invoice Reader",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Invoice Reader")

st.write("Welcome to your first AI product!")

uploaded_file = st.file_uploader(
    "Upload your invoice (PDF)",
    type=["pdf"]
)

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")