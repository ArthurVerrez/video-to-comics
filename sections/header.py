import streamlit as st
from constants import CURRENT_VERSION


def header():

    st.markdown(
        f"<h1>Video to Comics<small>{CURRENT_VERSION}</small></h1>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """Welcome! 👋 
        
        Drop a video of max 1 min and watch it get transformed into a comic panel ✨"""
    )

    st.divider()
