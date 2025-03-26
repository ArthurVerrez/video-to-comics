import streamlit as st
from constants import CURRENT_VERSION


def header():

    st.markdown(
        f"<h1>Video to Comics<small>{CURRENT_VERSION}</small></h1>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """Welcome! 👋 
        Drop a video of max 1 min and watch it get transformed into a comic panel ✨
        """
    )
    st.markdown(
        """
        As of now, it's still now possible to use the generation in the API, but we'll integrate it as soon as it comes out ([see communication](https://openai.com/index/introducing-4o-image-generation/))
        """,
    )

    st.divider()
