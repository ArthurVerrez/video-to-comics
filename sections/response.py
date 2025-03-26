import streamlit as st
from video_utils import get_full_video_description_with_dialogues
import tempfile
import os


def response():
    # Create a temporary file to store the uploaded video
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(st.session_state.video_file.getvalue())
        video_path = tmp_file.name

    try:
        # Display the video
        st.video(st.session_state.video_file)

        # Add a spinner while processing the video
        with st.spinner("Analyzing video content..."):
            # Get video description using the temporary file path
            description = get_full_video_description_with_dialogues(video_path)

            if description:
                st.markdown("### Video Description")
                st.write(description)
            else:
                st.error("Failed to analyze the video. Please try again.")

    finally:
        # Clean up the temporary file
        os.unlink(video_path)
