# Bukti Beda Skema vs Paper Existing (dikunci: Ganti Total)
Task spesifik: **Triase Tuntas** — cerita awam → 5 output wajib
(instansi + versi akta + ceklis dokumen + status + langkah berikutnya),
tidak boleh tutup sebelum slot lengkap.

## 1. vs LexID (Muninggar & Krisnadhi 2023, JIKI)
LexID = knowledge graph retrieval 20rb+ regulasi (metadata + isi pasal),
relasi antar-dokumen (amends/repeals/implements/hasLegalBasis),
evaluasi F1 retrieval. Tidak ada triase, tidak ada akta privat/PPAT.

| LexID | Notaris-Triage (ini) | Beda |
|---|---|---|
| `LegalDocument` + 33 subclass jenis regulasi | `Akta` + subclass versi layanan (AJB, Hibah, APHB, Fidusia, Wasiat, PT/CV, Kawin) | Domain regulasi vs domain layanan notaris |
| `Norm`, `RuleAct`, `Concept`, `CompoundExpression` | `KasusTriage`, `CeritaAwam`, `JenisTransaksi`, `StatusPenanganan` | Semantik pasal vs status triase awam |
| `hasLegalBasis`, `amends`, `repeals`, `implements` | `butuhAkta`, `ditanganiOleh`, `butuhDokumen`, `berstatus`, `saranLangkah` | Relasi dokumen vs relasi kebutuhan→solusi |
| `Person/Office/City`, PlaceOfPromulgation | `Tokoh` (WargaAwam/PejabatNotaris/PejabatPPAT/Saksi), `Lembaga` (Notaris/PPAT/Pengadilan/BPN/AHU/Dukcapil) | Metadata pengesahan vs aktor penanganan |
| Query: isi pasal / status amandemen | Query CQ1–CQ10: instansi + akta + kurang dokumen + estimasi | Retrieval vs triase tuntas |
| Tidak ada SWRL triase | 7 SWRL R1–R7 peristiwa→akta→status | Tidak ada inferensi kasus di LexID |

## 2. vs Loutas et al. 2011 (SemanticGov Portal)
Loutas = portal layanan publik umum (SIM, chamber of commerce),
Service Tree Ontology (STO) + Public Service Ontology + STL/QM,
fokus find-service + cek eligibility + versi layanan.

| Loutas | Notaris-Triage (ini) | Beda |
|---|---|---|
| `ServiceType` → `ServiceVersion` (layanan publik) | `JenisTransaksi` → `KasusTriage` + `StatusPenanganan` (kasus hukum) | Layanan admin vs peristiwa hukum |
| `InternalNode/LeafNode/Question/SparqlQuery` (STO meta) | Tidak dipakai; dialog = slot-filling per keperluan di `demo/app.py` | Struktur tree berbeda, nama berbeda |
| `Public Service Ontology` (GEA: SocietalEntity, Evidence, Outcome) | `Akta/DokumenSyarat/ObjekHukum/KomponenBiaya/AturanHukum` | Model layanan vs model akta-dokumen-biaya |
| Output: deskripsi layanan + eligibility | Output: 5 wajib triase + tolak tutup sebelum lengkap | Eligibility sekali vs pengawalan sampai tuntas |
| dievaluasi via prototype portal eGov | Dievaluasi via 10 CQ + 8 skenario `--test` + HermiT | Metrik berbeda |

## 3. vs B-Team 3 (proposal tim)
B-Team 3 = ide 4 lapis + tabel beda referensi, masih konsep
(belum ada OWL jalan, CQ, SPARQL, SWRL executable).
Ini = perwujudan executable-nya dengan kalimat, nama kelas,
dan 9 kasus contoh yang diparafrase baru.

## Cara verifikasi cepat (untuk dosen)
1. Protege → Search: `LegalDocument`, `Norm`, `ServiceTree` → **0 hasil** (tidak ada di skema ini).
2. Search: `KasusTriage`, `saranLangkah`, `butuhAkta` → ada (orisinal).
3. `python3 demo/app.py --test` → 8/8 deteksi + 10/10 CQ ada baris.
