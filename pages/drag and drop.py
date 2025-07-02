import streamlit as st
from streamlit_javascript import st_javascript
from pages.backend.Blocks import blocks

st.set_page_config(layout="wide")
st.title("🧠 Visual RAG Builder")

with open("pages/backend/test.html") as f:
    drawflow_html = f.read()

st.components.v1.html(drawflow_html, height=850)

if st.button("Get Flow JSON"):
    flow_json = st_javascript("return window.getFlow ? window.getFlow() : null;")
    if flow_json:
        st.subheader("Exported Flow JSON")
        st.json(flow_json)
    else:
        st.warning("No flow found. Please build your flow and try again.")