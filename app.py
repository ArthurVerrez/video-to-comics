import streamlit as st
from sections.metadata import metadata
from sections.header import header
from sections.footer import footer
from sections.sidebar import sidebar
from sections.input_form import input_form

metadata()
sidebar()
header()

input_form()
footer()
