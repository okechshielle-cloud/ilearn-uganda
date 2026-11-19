import streamlit as st

st.set_page_config(page_title="iLearn-Uganda Test")
st.title("iLearn-Uganda Smoke Test")
st.write("If you see this, Streamlit is rendering.")

try:
    import matplotlib
    import pandas as pd
    st.success(f"Imports OK — matplotlib {matplotlib.__version__}, pandas {pd.__version__}")
except Exception as e:
    st.error(f"Import failed: {e}")
