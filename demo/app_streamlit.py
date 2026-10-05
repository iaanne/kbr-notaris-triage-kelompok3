# UI web opsional (Streamlit). Logika tetap sama dengan app.py.
import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from app import deteksi, ground_case, CASE_IRI, SLOTS

st.title("Triase Notaris/PPAT")
st.caption("Jawaban diambil dari ontology. Lengkapi sampai tuntas.")

cerita = st.text_input("Ceritakan keperluan Anda (contoh: mau hibah tanah ke anak)")
if cerita:
    need = deteksi(cerita)
    st.info(f"Terdeteksi: {need}. Lengkapi slot berikut.")
    data = {}
    for key, tanya in SLOTS.get(need, []):
        data[key] = st.text_input(tanya, key=f"{need}-{key}")
    if st.button("Buatkan hasil triase"):
        if any(not v for v in data.values()):
            st.warning("Masih ada slot kosong. Lengkapi dulu.")
        else:
            info = ground_case(CASE_IRI[need])
            st.success(f"Instansi: {info['lembaga']} | Akta: {info['akta']} | Status: {info['status']}")
            st.write("Dokumen:", ", ".join(info["dokumen"]))
            st.write("Langkah:", info["saran"])
            st.write("Waktu:", info["waktu"], "Biaya:", info["biaya"])
            st.caption("Arahan awal, bukan pengganti Notaris/PPAT. Bawa ceklis ini saat datang.")
