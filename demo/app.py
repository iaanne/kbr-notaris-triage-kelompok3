# Demo triase Notaris/PPAT untuk pengguna awam.
# Prinsip: setiap jawaban diambil dari ontology via SPARQL, bukan karangan.
# Alur: isi slot sampai lengkap, lalu tutup dengan ceklis siap print.
# Jalankan: python3 app.py  (CLI)  |  python3 app.py --test  (uji skenario)
# Opsional Streamlit: streamlit run app_streamlit.py
import re, sys
from pathlib import Path

try:
    from rdflib import Graph
except ImportError:
    print("Butuh rdflib: pip install --break-system-packages rdflib")
    sys.exit(1)

BASE = Path(__file__).resolve().parent
ONTO = BASE.parent / "ontology" / "notaris-triage.ttl"

g = Graph()
g.parse(str(ONTO), format="turtle")

def q1(sparql):
    return list(g.query(sparql))

def ground_case(case_iri):
    """Ambil fakta ground-truth satu kasus dari ontology."""
    short = case_iri.split("#")[-1]
    Q = f"""
    PREFIX : <http://www.semanticweb.org/iaanne/ontologies/2026/notaris-triage#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?lembaga ?akta ?status ?saran ?waktu ?biaya WHERE {{
      :{short} :ditanganiOleh ?l ; :butuhAkta ?a ; :berstatus ?s ; :saranLangkah ?saran .
      ?l rdfs:label ?lembaga . ?a rdfs:label ?akta . ?s rdfs:label ?status .
      OPTIONAL {{ :{short} :perkiraanWaktu ?waktu . }}
      OPTIONAL {{ :{short} :perkiraanBiaya ?biaya . }}
    }}"""
    rows = q1(Q)
    docs_q = f"""
    PREFIX : <http://www.semanticweb.org/iaanne/ontologies/2026/notaris-triage#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?d WHERE {{ :{short} :butuhDokumen ?x . ?x rdfs:label ?d . }}"""
    docs = sorted({str(r[0]) for r in q1(docs_q)})
    if not rows:
        return None
    r = rows[0]
    return {"lembaga": str(r[0]), "akta": str(r[1]), "status": str(r[2]),
            "saran": str(r[3]), "waktu": str(r[4] or "-"), "biaya": str(r[5] or "-"),
            "dokumen": docs}

# --- Deteksi keperluan dari bahasa sehari-hari (keyword, bisa diganti NLP/LLM) ---
POLA = [
    ("waris_sengketa", ["ribut", "tidak setuju", "tidak sepakat", "sengketa", "rebutan", "beda agama", "menolak"]),
    ("waris_jual", ["waris", "warisan", "ahli waris", "peninggalan", "balik nama waris", "belum balik nama"]),
    ("hibah", ["hibah", "kasih ke anak", "pemberian cuma", "hadiah tanah"]),
    ("usaha", ["usaha", "pt perorangan", "pt biasa", " cv", "bikin pt", "dirikan", "umkm", "badan usaha"]),
    ("fidusia", ["utang", "pinjam", "jaminan", "fidusia", "bpkb", "jaminan motor", "kredit"]),
    ("wasiat", ["wasiat", "pesan terakhir", "meninggal nanti", "tidak rebutan"]),
    ("kawin", ["kawin", "nikah", "pisah harta", "harta bersama", "perjanjian kawin", "pra-nikah"]),
    ("jualbeli", ["jual", "beli", "ajb", "balik nama", "shm", "sertifikat", "tanah"]),
]

CASE_IRI = {
    "jualbeli": "kasus_jualbeli_shm",
    "waris_jual": "kasus_waris_belumSKW",
    "waris_sengketa": "kasus_waris_sengketa",
    "hibah": "kasus_hibah_tanah",
    "usaha_pt": "kasus_ptperorangan",
    "usaha_cv": "kasus_cv",
    "fidusia": "kasus_fidusia_motor",
    "wasiat": "kasus_wasiat",
    "kawin": "kasus_kawin",
}

# Slot yang harus diisi per keperluan (slot-filling sampai tuntas)
SLOTS = {
    "jualbeli": [("sertifikat", "Apakah sertifikat (SHM/HGB) sudah atas nama penjual? (sudah/belum)"),
                  ("sepakat", "Apakah penjual-pembeli dan pasangan masing-masing sudah sepakat harga? (sudah/belum)"),
                  ("dok", "Apakah KTP, KK, PBB lunas, dan SHM asli sudah di tangan? (sudah/belum)")],
    "waris_jual": [("skw", "Apakah Surat Keterangan Waris (SKW) sudah ada? (sudah/belum)"),
                   ("sepakat", "Apakah SEMUA ahli waris setuju dijual? (sudah/belum)"),
                   ("sertifikat", "Apakah sertifikat tanahnya ada? (sudah/belum)")],
    "waris_sengketa": [("sepakat", "Apakah semua ahli waris sepakat? (sudah/belum)")],
    "hibah": [("sertifikat", "Apakah SHM atas nama pemberi hibah? (sudah/belum)"),
              ("hubungan", "Apakah penerima masih keluarga (anak/pasangan)? (ya/bukan)")],
    "usaha_pt": [("pendiri", "Berapa orang pendirinya? (1/2+)"),
                 ("modal", "Apakah modal kecil/UMKM? (ya/tidak)")],
    "usaha_cv": [("pendiri", "Berapa orang sekutunya? (tulis angka)")],
    "fidusia": [("bpkb", "Apakah BPKB/faktur ada? (sudah/belum)"),
                ("utang", "Apakah ada perjanjian utang pokoknya? (sudah/belum)")],
    "wasiat": [("sehat", "Apakah pemberi wasiat sehat jasmani dan cakap hukum? (ya/tidak)"),
               ("saksi", "Apakah ada 2 saksi yang bisa hadir? (sudah/belum)")],
    "kawin": [("nikah", "Sudah menikah atau baru rencana? (sudah/rencana)"),
              ("sepakat", "Apakah pasangan sepakat pisah harta? (sudah/belum)")],
}

def deteksi(cerita):
    t = cerita.lower()
    # sengketa didahulukan agar tidak ketelan waris_jual
    for key, kws in POLA:
        for kw in kws:
            if kw in t:
                if key == "waris_sengketa":
                    return "waris_sengketa"
                if key == "waris_jual":
                    return "waris_jual"
                if key == "usaha":
                    # bedakan PT perorangan vs CV dari jumlah pendiri nanti; default tanya
                    if "perorangan" in t or "sendiri" in t or "seorang" in t:
                        return "usaha_pt"
                    if " berdua" in t or " cv" in t or "dua orang" in t:
                        return "usaha_cv"
                    return "usaha_pt"  # default, dikoreksi saat slot pendiri diisi
                return key
    return "jualbeli"  # default paling umum

def sapa_awal(need, info):
    judul = {"jualbeli": "jual-beli tanah", "waris_jual": "jual tanah warisan",
             "waris_sengketa": "bagi waris bersengketa", "hibah": "hibah tanah",
             "usaha_pt": "dirikan PT perorangan", "usaha_cv": "dirikan CV",
             "fidusia": "utang dengan jaminan", "wasiat": "buat wasiat",
             "kawin": "atur harta kawin"}.get(need, need)
    print(f"\nKebutuhan tercatat: {judul}.")
    print("Alur: cek syarat > ceklis dokumen > instansi dan akta > langkah berikutnya.")
    print("Jawab singkat (sudah/belum/ya/tidak/angka). Ketik 'batal' untuk berhenti.\n")

def tanya_slot(need, jawaban_awal=None):
    data = dict(jawaban_awal or {})
    slots = SLOTS[need]
    # izinkan koreksi usaha_pt -> usaha_cv bila pendiri >= 2
    for key, pertanyaan in slots:
        if key in data:
            continue
        print("BOT:", pertanyaan)
        j = input("Anda: ").strip().lower()
        if j == "batal":
            return None
        data[key] = j
        if need == "usaha_pt" and key == "pendiri" and j.strip().startswith("2"):
            print("BOT: Pendiri 2 orang atau lebih, dialihkan ke jalur CV/PT biasa.")
            return {"__alih__": "usaha_cv", **data}
    return data

def putusan(need, data):
    """Terapkan logika SWRL secara ringkas (mirror dari ontology) + grounding SPARQL."""
    # Aturan sengketa: tidak sepakat -> pengadilan
    sepakat = (data.get("sepakat") or "")
    if need in ("waris_jual", "waris_sengketa") and sepakat.startswith(("belum", "tidak", "t")) and "sudah" not in sepakat and "ya" not in sepakat:
        need = "waris_sengketa"
    if need == "waris_jual" and data.get("skw", "").startswith(("belum", "t", "b")) and "sudah" not in data.get("skw", ""):
        pass  # tetap waris_jual dengan status belum lengkap (sesuai R2)
    iri = CASE_IRI[need]
    info = ground_case(iri)
    return need, info

def cetak_tuntas(need, data, info):
    print("\n----- HASIL TRIASE -----")
    print(f"Keperluan   : {need}")
    print(f"Instansi    : {info['lembaga']}")
    print(f"Akta/surat  : {info['akta']}")
    print(f"Status      : {info['status']}")
    print("Dokumen yang harus disiapkan:")
    for d in info["dokumen"]:
        print(f"  - {d}")
    print(f"Jawaban Anda: {data}")
    print(f"Langkah berikutnya: {info['saran']}")
    print(f"Perkiraan waktu : {info['waktu']}")
    print(f"Perkiraan biaya : {info['biaya']}")
    print("Dasar hukum (umum, konfirmasi ke pejabat): UUJN No.2/2014; aturan PPAT; KUHPerdata/KHI untuk waris; UU Fidusia/PT/Perkawinan sesuai kasus.")
    print("Catatan: ini arahan awal, bukan pengganti Notaris/PPAT. Bawa ceklis ini saat datang.")
    print("------------------------\n")

def main():
    print("Layanan triase Notaris/PPAT.")
    print("Ceritakan keperluan dengan bahasa sehari-hari. Contoh: 'mau jual tanah warisan belum balik nama'.")
    cerita = input("Anda: ").strip()
    if not cerita:
        print("BOT: Cerita kosong. Ulangi.")
        return
    need = deteksi(cerita)
    if need == "usaha_pt":
        print("BOT: Untuk usaha, pastikan dulu jumlah pendirinya.")
    sapa_awal(need, None)
    data = tanya_slot(need)
    if data is None:
        print("BOT: Sesi dibatalkan.")
        return
    if "__alih__" in data:
        need = data.pop("__alih__")
        sapa_awal(need, None)
        data2 = tanya_slot(need, data)
        if data2 is None:
            return
        data = data2
    need_fix, info = putusan(need, data)
    if info is None:
        print("BOT: Data tidak ditemukan di ontology. Ceritakan ulang.")
        return
    cetak_tuntas(need_fix, data, info)
    print("BOT: Ada yang kurang jelas? (tulis pertanyaan / 'selesai')")
    while True:
        j = input("Anda: ").strip().lower()
        if j in ("selesai", "cukup", "tidak", "ok"):
            print("BOT: Sesi selesai. Simpan hasil di atas untuk dibawa ke pejabat.")
            break
        print("BOT: Patokannya tetap ceklis di atas. Bawa dokumennya, tanyakan ke pejabat yang tercantum. ('selesai' untuk tutup)")

def test():
    cases = [
        ("mau jual tanah shm", "jualbeli"),
        ("mau jual tanah warisan belum balik nama", "waris_jual"),
        ("ahli waris ribut tidak sepakat", "waris_sengketa"),
        ("mau hibah tanah ke anak", "hibah"),
        ("mau bikin pt perorangan sendiri", "usaha_pt"),
        ("utang jaminan motor bpkb", "fidusia"),
        ("mau buat wasiat", "wasiat"),
        ("mau perjanjian pisah harta nikah", "kawin"),
    ]
    ok = 0
    for cerita, harap in cases:
        got = deteksi(cerita)
        info = ground_case(CASE_IRI.get(got, "kasus_jualbeli_shm"))
        lolos = (got == harap) and (info is not None)
        print(f"[{'OK' if lolos else 'FAIL'}] '{cerita}' -> {got} (harap {harap}) | {info['lembaga']} / {info['akta']}" if info else "no info")
        ok += lolos
    print(f"\n{ok}/{len(cases)} deteksi + grounding lolos.")
    # uji CQ count
    print("Uji 10 CQ:", end=" ")
    import glob
    n = 0
    for f in sorted(glob.glob(str(BASE.parent / 'queries' / '*.rq'))):
        if list(g.query(open(f, encoding='utf-8').read())):
            n += 1
    print(f"{n}/10 query mengembalikan baris.")

if __name__ == "__main__":
    if "--test" in sys.argv:
        test()
    else:
        main()
