"""Verbalisasi: ontology dan aturan SWRL -> kalimat bahasa awam.

Aturan main: tidak ada kalimat yang dikarang dari luar ontology. Setiap baris
keluaran membawa `sumber` triple aslinya, sehingga jawaban yang muncul di UI
bisa ditelusuri balik ke baris .ttl dan ke pasal yang jadi dasarnya.

Jalankan:
    python3 -m notaris.verbalisasi            # tulis data/verbalized.jsonl
    python3 -m notaris.verbalisasi --cek      # ringkasan saja, tanpa tulis
"""

from __future__ import annotations

import json
import sys

from rdflib import Graph
from rdflib.namespace import OWL, RDF

from . import DATA
from .ontology import (
    Atom,
    Aturan,
    NS,
    label,
    muat_ontology,
    muat_aturan,
    nama_lokal,
    nilai_teks,
    variabel_kasus,
)

KELUARAN = DATA / "verbalized.jsonl"


# --------------------------------------------------------------------------
# Kamus kalimat
# --------------------------------------------------------------------------

#: Kalimat baku per object property. Slot `{s}` dan `{o}` diisi label.
KALIMAT_OBJ = {
    "ditanganiOleh": "{s} ditangani oleh {o}.",
    "butuhAkta": "{s} butuh akta {o}.",
    "butuhDokumen": "{s} butuh dokumen {o}.",
    "sudahPunyaDokumen": "{s} sudah punya dokumen {o}.",
    "berstatus": "Status {s} adalah {o}.",
    "punyaJenis": "{s} berkategori {o}.",
    "punyaObjek": "{s} berobjek {o}.",
    "dikenaiBiaya": "{s} dikenai biaya {o}.",
    "melibatkanTokoh": "{s} melibatkan {o}.",
    "menangani": "{s} menangani {o}.",
    "menceritakan": "Kisah {s} berkaitan dengan {o}.",
    "perluDaftarDi": "{s} perlu didaftarkan di {o}.",
    "aktaUntuk": "Akta {s} berguna untuk {o}.",
    "berdasarPada": "{s} bersandar pada {o}.",
    "dasarKasus": "{s} memperoleh dasar dari {o}.",
    "terkaitAturan": "{s} terkait {o}.",
    "sudahPunyaSertifikat": "{s} sudah punya sertifikat.",
}

#: Kalimat untuk data property yang isinya kalimat panjang.
KALIMAT_ISI = {
    "perkiraanWaktu": "Perkiraan waktu {s}: {o}",
    "perkiraanBiaya": "Perkiraan biaya {s}: {o}",
    "saranLangkah": "Langkah berikutnya untuk {s}: {o}",
}

#: Kalimat untuk slot boolean yang harus dijawab pengguna. `{v}` -> ya/tidak.
KALIMAT_SLOT = {
    "adaSertifikat": "Sertifikat (SHM/HGB) sudah atas nama pemilik: {v}.",
    "adaSKWaris": "Sudah ada Surat Keterangan Waris: {v}.",
    "adaSepakat": "Semua pihak sudah sepakat: {v}.",
    "cakapHukum": "Orang concerned cakap hukum: {v}.",
    "modalKecil": "Modal usaha termasuk kecil: {v}.",
    "adaSertifikatTanah": "Sertifikat tanah sudah ada: {v}.",
    "sudahPunyaSKW": "Surat Keterangan Waris sudah ada: {v}.",
}

#: Template utuh per slot, dipakai saat Composite pertanyaan chel di UI.
PERTANYAAN_SLOT = {
    "adaSertifikat": "Apakah sertifikat (SHM/HGB) sudah atas nama penjual?",
    "adaSKWaris": "Apakah Surat Keterangan Waris (SKW) sudah ada?",
    "adaSepakat": "Apakah semua pihak sudah sepakat?",
    "cakapHukum": "Apakah yang berkepentingan sehat dan cakap hukum?",
    "modalKecil": "Apakah modalnya kecil atau UMKM?",
    "jumlahPendiri": "Berapa orang pendirinya?",
}


def _bool_teks(nilai) -> str:
    return "ya" if nilai else "tidak"


def verbalisasi_individu(g: Graph) -> list[dict]:
    """`penjelasanAwam` jadi kalimat utuh, satu baris per entitas.

    Satu entitas satu baris, bukan satu baris per jenis domain: sebelumnya
    pengelompokan per domain membuat 56 penjelasan terhitung tujuh kali
    (56 x 7 = 392 baris yang isinya kembar).
    """
    hasil = []
    for s, _, o in sorted(
        g.triples((None, NS.penjelasanAwam, None)),
        key=lambda t: (nama_lokal(t[0]), str(t[2])),
    ):
        hasil.append(
            {
                "id": f"penjelasan:{nama_lokal(s)}",
                "teks": str(o),
                "jenis": "penjelasan",
                "sumber": {
                    "subjek": nama_lokal(s),
                    "predikat": "penjelasanAwam",
                    "objek": str(o),
                    "label_subjek": label(g, s),
                    "kelas": sorted(nama_lokal(t) for t in g.objects(s, RDF.type) if t != OWL.NamedIndividual),
                },
            }
        )
    return hasil


def verbalisasi_fakta(g: Graph) -> list[dict]:
    """Satu kalimat per triple domain: kasus, akta, biaya, dan pejabat."""
    hasil = []
    orderly = sorted(
        g.triples((None, None, None)),
        key=lambda t: (nama_lokal(t[0]), nama_lokal(t[1]), nama_lokal(t[2])),
    )
    for s, p, o in orderly:
        nama_p = nama_lokal(p)
        if p == NS.penjelasanAwam:
            continue  # sudah ditangani verbalisasi_individu
        if p == RDF.type or p.rsplit("#", 1)[-1] in ("label", "comment", "domain", "range", "subClassOf"):
            continue

        kalimat = None
        if nama_p in KALIMAT_ISI:
            kalimat = KALIMAT_ISI[nama_p]
        elif nama_p in KALIMAT_SLOT and isinstance(o, bool):
            kalimat = KALIMAT_SLOT[nama_p].replace("{v}", _bool_teks(o))
        elif nama_p in KALIMAT_OBJ:
            kalimat = KALIMAT_OBJ[nama_p]
        if kalimat is None:
            continue

        hasil.append(
            {
                "id": f"fakta:{nama_lokal(s)}:{nama_p}:{nama_lokal(o)}",
                "teks": kalimat.format(s=label(g, s), o=label(g, o) if not isinstance(o, bool) else ""),
                "jenis": "fakta",
                "sumber": {
                    "subjek": nama_lokal(s),
                    "predikat": nama_p,
                    "objek": nama_lokal(o) if not isinstance(o, bool) else nilai_teks(o),
                    "label_subjek": label(g, s),
                    "label_objek": "" if isinstance(o, bool) else label(g, o),
                },
            }
        )
    return hasil


def _teks_atom(g: Graph, atom: Atom) -> str:
    """Satu atom jadi fragmen kalimat."""
    pred = atom.nama_predikat
    if atom.jenis == "kelas":
        return f"bertipe {label(g, atom.predikat)}"
    if atom.jenis == "nilai":
        nilai = atom.argumen2
        if isinstance(nilai, bool):
            return f"{label(g, atom.predikat)} = {_bool_teks(nilai)}"
        return f"{label(g, atom.predikat)} = {nilai_teks(nilai)}"
    return f"{label(g, atom.predikat)} = {label(g, atom.argumen2)}"


def verbalisasi_aturan(g: Graph, aturan: Aturan) -> dict:
    """Satu aturan SWRL -> blok JIKA/MAKA yang bisa dibaca manusia."""
    body_teks = []
    for atom in aturan.body:
        if atom.jenis == "kelas":
            body_teks.append(f"kasus adalah {label(g, atom.predikat)}")
        else:
            body_teks.append(_teks_atom(g, atom))
    head_teks = [_teks_atom(g, atom) for atom in aturan.head]

    return {
        "id": f"aturan:{aturan.nama}",
        "teks": (
            f"{aturan.label} "
            f"JIKA {' DAN '.join(body_teks)} MAKA {' DAN '.join(head_teks)}."
        ),
        "jenis": "aturan",
        "sumber": {
            "aturan": aturan.nama,
            "label": aturan.label,
            "syarat": body_teks,
            "kesimpulan": head_teks,
        },
    }


def verbalisasi_aturan_pertanyaan(g: Graph, aturan: Aturan) -> list[dict]:
    """Slot yang harus dijawab pengguna, diambil langsung dari `swrl:body`."""
    hasil = []
    for atom in aturan.body:
        if atom.jenis != "nilai":
            continue
        nama = atom.nama_predikat
        if nama not in PERTANYAAN_SLOT:
            continue
        hasil.append(
            {
                "id": f"slot:{aturan.nama}:{nama}",
                "teks": f"{PERTANYAAN_SLOT[nama]} (jawaban: sudah/belum, ya/tidak, atau angka)",
                "jenis": "slot",
                "sumber": {"aturan": aturan.nama, "slot": nama, "label": PERTANYAAN_SLOT[nama]},
            }
        )
    return hasil


def bangun(g: Graph | None = None) -> dict:
    """Bangun seluruh korpus verbalisasi."""
    g = g or muat_ontology()
    var = variabel_kasus(g)
    baris: list[dict] = []
    baris += verbalisasi_individu(g)
    baris += verbalisasi_fakta(g)
    for aturan in muat_aturan(g).values():
        baris.append(verbalisasi_aturan(g, aturan))
        baris += verbalisasi_aturan_pertanyaan(g, aturan)
    return {"jumlah": len(baris), "baris": baris}


def main() -> int:
    cek = "--cek" in sys.argv
    korpus = bangun()
    if cek:
        print(f"{korpus['jumlah']} baris verbalisasi.")
        for b in korpus["baris"][:8]:
            print(f"  [{b['jenis']:9}] {b['teks'][:88]}")
        return 0

    KELUARAN.parent.mkdir(parents=True, exist_ok=True)
    with KELUARAN.open("w", encoding="utf-8") as f:
        for b in korpus["baris"]:
            f.write(json.dumps(b, ensure_ascii=False) + "\n")
    print(f"{korpus['jumlah']} baris -> {KELUARAN.relative_to(DATA.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())