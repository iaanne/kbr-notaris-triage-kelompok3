# Notaris Triage

## Isi
- `ontology/notaris-triage.ttl` — OWL DL (31 kelas + 1 union, 16 object property, 10 data property,
  9 kasus ABox, 8 aturan SWRL sebagai swrl:Imp). Dibuka di Protege.
- `queries/cq01..cq10.rq` — 10 SPARQL untuk 10 competency questions.
- `rules/swrl-rules.md` — 8 aturan versi manusia + sumber pasal.
- `docs/TRACEABILITY.md` — pasal → ontology → rule → CQ.
- `docs/SKEMA-BEDA.md` — bukti beda skema vs LexID/Loutas/B-Team3.
- `docs/EVALUASI-CQ.md` — hasil uji aktual.
- `demo/app.py` — chatbot CLI solution-oriented (slot-filling + grounding SPARQL
  + ceklis akhir). Bukan sekadar Q&A: menolak tutup sebelum slot lengkap.

## Cara pakai cepat
1. Protege: buka `ontology/notaris-triage.ttl`, nyalakan HermiT, coba Queries CQ.
2. Uji otomatis: `python3 demo/app.py --test` (butuh `pip install --break-system-packages rdflib`)
3. Chatbot: `python3 demo/app.py`, contoh input: `mau jual tanah warisan belum balik nama`
4. Streamlit (opsional): `streamlit run demo/app_streamlit.py`

## Beda dari referensi
- vs LexID (Muninggar 2023): LexID = retrieval 20rb regulasi; ini = triase
  instansi/akta/dokumen + SWRL + bahasa awam. LexID hanya jadi inspirasi layer aturan.
- vs Loutas 2011: Loutas = portal layanan publik umum + STO; ini = domain
  notaris/PPAT + Triage Tree + grounding ontology per kasus.
- vs B-Team 3: B-Team 3 masih proposal; ini mewujudkan OWL jalan + CQ + demo.

## Batasan jujur
Desk research, bukan nasihat hukum final. Estimasi biaya/waktu umum dan bisa
berubah. Selalu konfirmasi ke Notaris/PPAT/BPN/AHU. Belum mencakup sengketa
kompleks, pajak detail per daerah, dan putusan pengadilan.
