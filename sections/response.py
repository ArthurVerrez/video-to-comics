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
            description, messages = get_full_video_description_with_dialogues(
                video_path
            )

            if description:
                st.markdown("### Video Description")
                st.write(description)
            else:
                st.error("Failed to analyze the video. Please try again.")

            # Display messages with toggle
            if messages:
                with st.expander("Show all messages", expanded=False):
                    for i, message in enumerate(messages):
                        st.markdown(f"**Message {i+1}:**")

                        # Handle different content types
                        content = message.get("content", "")
                        if isinstance(content, list):
                            # Handle list content (text + image)
                            for item in content:
                                if item.get("type") == "image_url":
                                    # Display base64 image
                                    st.markdown(
                                        f"<img src='{item['image_url']['url']}' style='max-width:100%;'>",
                                        unsafe_allow_html=True,
                                    )
                                elif item.get("type") == "text":
                                    # Display text content
                                    st.write(item.get("text", "No text content"))
                        else:
                            # Handle string content
                            if content.startswith("data:image"):
                                # Display base64 image
                                st.markdown(
                                    f"<img src='{content}' style='max-width:100%;'>",
                                    unsafe_allow_html=True,
                                )
                            else:
                                # Display text message
                                st.write(content)

                        st.divider()
    finally:
        # Clean up the temporary file
        os.unlink(video_path)


# Using the images and the text, give me a detailed description, panel by panel, of how you would create a comic panel composed of 6 frames, 2 per row, in the style of ghibli animation
# If relevant, include text bubbles and associated text

# FRAME 1:....
