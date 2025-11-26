"""
Untuk jalankan,

streamlit run Tugas_AI_Hactive8.py
"""

import os

import pandas as pd
import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Bikin judul
st.title("Update Raport Siswa")

# Cek apakah API key sudah ada
if "GOOGLE_API_KEY" not in os.environ:
    # Jika belum, minta user buat masukin API key
    google_api_key = st.text_input("Google API Key", type="password")
    # User harus klik Start untuk save API key
    start_button = st.button("Start")
    if start_button:
        os.environ["GOOGLE_API_KEY"] = google_api_key
        st.rerun()
    # Jangan tampilkan chat dulu kalau belum pencet start
    st.stop()

# Inisiasi client LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Pilih user adalah Guru atau Orang Tua Siswa

if "participant_status" not in st.session_state:
    if st.button("Guru"):
        st.session_state["participant_status"] = "Guru"
        st.rerun()
    elif st.button("Orang Tua Siswa"):
        st.session_state["participant_status"] = "Ortu"
        st.rerun()
    st.stop()

option = st.session_state["participant_status"]


# Fungsi upload nilai
def upload_nilai(label, key):
    uploaded_ujian = st.file_uploader(label, type=["xls", "xlsx"], key=key)
    if uploaded_ujian:
        hasil_ujian = pd.read_excel(uploaded_ujian)
        st.session_state["participant_resume"] = hasil_ujian
        st.success("Nilai siswa berhasil diupload.")
        st.session_state["call_guru_triggered"] = False  # Reset flag setelah upload!
        st.rerun()
    st.stop()

# --- Pengecekan awal: jika sudah ada data, langsung ke next step ---
if "participant_resume" in st.session_state:
    if option == "Guru":
        # analisa/flow berikutnya di sini
        nilai = st.session_state["participant_resume"]
        data_nilai_str = nilai.to_markdown(index=False)
        analisa_nilai = ("Analisa dari file upload. Nama2 mata pelajaran yang rata2nya dibawah 50, nama2 siswa yang rata2 nilainya dibawah 50, apa yang harus diperbaiki oleh siswa berdasarkan evaluasi kualitatif guru dan provide analysis dalam bullet points tidak lebih dari 20 baris")
        system_message = SystemMessage(analisa_nilai+data_nilai_str)
        human_message = HumanMessage("Tolong lakukan analisa seperti instruksi analisa_nilai")
        messages_history = (system_message, human_message)
        response = llm.invoke(messages_history)
        st.markdown(response.content)
    if option == "Ortu":
        nilai = st.session_state["participant_resume"]
        st.success("Nilai siswa sudah tersedia!")

if "participant_resume" not in st.session_state:
    # --- Alur Ortu ---
    if option == "Ortu":
        # Flag trigger upload
        if "call_guru_triggered" not in st.session_state:
            st.session_state["call_guru_triggered"] = False

        if not st.session_state["call_guru_triggered"]:
            st.warning("Nilai belum tersedia, silakan kontak Guru dan minta upload nilai.")
            if st.button("Call Guru"):
                st.session_state["call_guru_triggered"] = True
                st.rerun()
            st.stop()

        # Setelah Call Guru ditekan (flag aktif), tampilkan uploader
        if st.session_state["call_guru_triggered"]:
            upload_nilai("Guru upload nilai siswa (Excel)", "callguru_upload")

    # --- Alur Guru ---
    if option == "Guru":
        upload_nilai("Masukkan Excel Hasil Ujian", "guru_upload")
    st.stop()


#Masukan Nama Siswa
prompt = st.chat_input("Masukkan nama siswa")
if not prompt:
        st.stop()
# Jika user ada prompt, tampilkan promptnya langsung
with st.chat_message("User"):
        st.markdown(prompt)

if option == "Guru":
    # Cek apakah data sebelumnya ttg message history sudah ada
    if "messages_history" not in st.session_state:
        # Jika belum, bikin datanya, isinya hanya system message dulu, dengan resume sebagai context
        st.session_state["messages_history"] = [
            SystemMessage(
                "Extract informasi nilai siswa dan berikan pendapat siswa mana yang harus memperbaiki nilai dan yang terbaik \n\n{}".format(nilai)
                        )
        ]
    # Jika messages_history sudah ada, tinggal di load aja
elif option == "Ortu":
    # Cek apakah data sebelumnya ttg message history sudah ada
    if "messages_history" not in st.session_state:
        # Jika belum, bikin datanya, isinya hanya system message dulu, dengan resume sebagai context
        st.session_state["messages_history"] = [
            SystemMessage(
                "Informasikan nilai siswa tersebut saja dan analisis siswa dengan masukan dari evaluasi guru sebaiknya apa yang siswa atau orang tua mesti perbaiki maksimal 100 baris atau 500 kata \n\n{}".format(nilai)
                        )
        ]
    # Jika messages_history sudah ada, tinggal di load aja     
messages_history = st.session_state["messages_history"]

# Masukin prompt ke message history, dan kirim ke LLM
messages_history.append(HumanMessage(prompt))
response = llm.invoke(messages_history)

# Simpan jawaban LLKM ke message history
messages_history.append(response)
# Tampilkan langsung jawaban LLM
with st.chat_message("AI"):
    st.markdown(response.content)
