# Log Progress Mingguan — untuk laporan dosen & dokumentasi
## Minggu 1 — Proposal + referensi (SELESAI, sebelum build)
- Proposal revisi B-Team 3 (stakeholder awam, ide KB 4 lapis, SDG 16/10/9).
- Referensi terkumpul: LexID JIKI 2023, Loutas SemanticGov 2011, 8 PPT dosen.

## Minggu 2 — Model KB v0.1 (SELESAI)
- `ontology/notaris-triage.ttl`: 849 triple, 30 kelas, 16 object property,
  10 data property, 9 kasus ABox, 7 SWRL.
- Bukti: lolos parse rdflib; OWL-RL expand 849→1847 tanpa error.

## Build ini — v0.2.0 Task Triase Tuntas + Skema Ganti Total (SELESAI, hari ini)
1. Header ontology dikunci: task Triase Tuntas (5 output wajib, tolak tutup
   sebelum slot lengkap) + pernyataan skema orisinal.
2. Baru: `docs/SKEMA-BEDA.md` — tabel side-by-side vs LexID, vs Loutas,
   vs B-Team 3 + cara verifikasi 3 langkah di Protege.
3. `docs/TRACEABILITY.md` dibetulkan (typo + pernyataan task).
4. `README.md` menautkan SKEMA-BEDA.
5. Verifikasi ulang (angka untuk laporan):
   - Triple: 849; SWRL: 7; CQ: 10/10 ada baris; demo `--test`: 8/8 OK.
   - Cek kontaminasi skema: LegalDocument/RuleAct/ServiceTree/PublicService → BERSIH TOTAL.
   - Simulasi interaktif warisan (belum/sudah/sudah) → status `belum lengkap` + suruh urus SKW dulu (benar).

## Bukti yang bisa dibawa ke dosen minggu ini
1. Screenshot Protege: Class hierarchy + HermiT "consistent".
2. Screenshot tab SPARQL: jalankan `queries/cq02-waris-jual.rq`.
3. Screenshot terminal: `python3 demo/app.py --test` (8/8 + 10/10).
4. Tunjukkan `docs/SKEMA-BEDA.md` sebagai jawaban "skema tidak sama dengan paper".

## Berikutnya (belum dikerjakan)
- Uji HermiT manual di Protege (butuh GUI, tidak bisa via CLI).
- Tambah kasus bila dosen minta (mis. HGB, waris Islam vs perdata dipisah).
- Lembar validasi notaris (opsional, bila diminta).
- Laporan akhir + slide.

## Build fix — presisi model (hari ini)
1. Domain/range: diverifikasi 16/16 object property + 10/10 data property lengkap;
   `penjelasanAwam` diperketat dari `owl:Thing` menjadi union 7 kelas pemakai.
2. R7 diluruskan (wasiat saja) + R8 baru untuk perjanjian kawin → 8 SWRL;
   body rule yang terlepas saat save Protege dibangun ulang dari nol.
3. SKMHT/APHT dipisah presisi hukum (UUHT 4/1996): `AktaHakTanggungan`
   (akta pokok, PPAT, daftar BPN) vs `SuratKuasaMembebankan` (kuasa
   pendahulu, tidak didaftar, wajib disusul APHT); tambah `aturan_uuht`.
   Verifikasi: 1007 triple, 8 SWRL, CQ 10/10, demo 8/8, RL expand OK.
