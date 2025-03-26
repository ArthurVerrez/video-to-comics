from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from sections.metadata import metadata
from sections.header import header
from sections.footer import footer
from sections.sidebar import sidebar
from sections.input_form import input_form
from sections.response import response


metadata()
sidebar()
header()

input_form()

if (
    st.session_state.api_key is not None
    and st.session_state.video_file is not None
    and st.session_state.instructions is not None
):
    response()


footer()
