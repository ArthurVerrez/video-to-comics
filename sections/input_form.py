import os
import streamlit as st


def input_form():
    form = st.form("agent_form")
    st.session_state.api_key = form.text_input(
        "OpenAI API Key _(only used during this session)_",
        type="password",
        value=os.getenv("OPENAI_API_KEY") or "",
    )
    st.session_state.instructions = form.text_input(
        "Custom style", value="ghibli animation"
    )

    # Add video file uploader
    st.session_state.video_file = form.file_uploader(
        "Upload a video file",
        type=["mp4", "avi", "mov", "mkv"],
        help="Supported formats: MP4, AVI, MOV, MKV",
    )

    form.form_submit_button("Submit", type="primary")
