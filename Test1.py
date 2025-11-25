"""
Untuk jalankan,

streamlit run app1.py
"""

import streamlit as st

st.title("My ChatBot Assistant")

nama = st.text_input("Masukkan nama anda")
if nama != "":
    st.markdown(f"Halo {nama}")

umur = st.slider("Umur", min_value=10, max_value=50)
st.markdown(f"Umur: {umur}")

submit_pressed = st.button("Submit")
if submit_pressed:
    st.balloons()