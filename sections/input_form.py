import os
import streamlit as st
from constants import LLM_OPTIONS


def input_form():
    form = st.form("agent_form")
    st.session_state.api_key = form.text_input(
        "OpenAI API Key _(only stored in your browser during this session)_",
        type="password",
        value=os.getenv("OPENAI_API_KEY") or "",
    )
    st.session_state.instructions = form.text_area(
        "Enter your instructions style instructions", height=100
    )

    form.form_submit_button("Submit", type="primary")
