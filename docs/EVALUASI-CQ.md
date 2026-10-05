# Evaluasi 10 CQ — hasil aktual (rdflib, 2026-10-05)
Ontology: ontology/notaris-triage.ttl (849 triple). Semua query mengembalikan baris.

| CQ | File | Hasil |
|---|---|---|
| CQ1 jual beli | cq01-jualbeli.rq | 1 baris: PPAT / AJB / siap ke PPAT |
| CQ2 waris jual | cq02-waris-jual.rq | 3 baris dokumen kurang + saran urus SKW |
| CQ3 sengketa | cq03-sengketa.rq | 1 baris: pengadilan / rujuk |
| CQ4 hibah | cq04-hibah.rq | 3 baris: akta hibah + biaya + daftar BPN |
| CQ5 usaha | cq05-usaha.rq | 2 baris: PT perorangan vs CV |
| CQ6 fidusia | cq06-fidusia.rq | 1 baris: notaris / fidusia |
| CQ7 wasiat | cq07-wasiat.rq | 1 baris: wasiat |
| CQ8 kawin | cq08-kawin.rq | 1 baris: perjanjian kawin + Dukcapil |
| CQ9 kelengkapan | cq09-kelengkapan.rq | 19 baris status + kurang + sudah |
| CQ10 biaya waktu | cq10-biaya-waktu.rq | 9 baris saran + waktu + biaya |

Cara ulang: `python3 demo/app.py --test`
Buka di Protege: File → Open → notaris-triage.ttl; jalankan HermiT via Reasoner;
uji SPARQL via tab SPARQL; aturan via tab SWRL (rule_R1..R7).
