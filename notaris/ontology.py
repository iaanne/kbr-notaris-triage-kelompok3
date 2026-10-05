"""Pembacaan ontology Notaris Triage.

Satu-satunya tempat di proyek ini yang tahu bentuk RDF yang dipakai: nama
lokal, label bahasa Indonesia, cakupan `penjelasanAwam`, dan aturan SWRL.
Modul lain membangun di atas sini dan tidak menyentuh rdflib langsung.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS

from . import TTL

NS = Namespace("http://www.semanticweb.org/iaanne/ontologies/2026/notaris-triage#")
SWRL = Namespace("http://www.w3.org/2003/11/swrl#")

#: Cadangan kalau deklarasi variabel di .ttl tidak terbaca.
VAR_KASUS = NS.var_k


def muat_ontology(jalur: str | Path = TTL) -> Graph:
    """Parse file Turtle. One-shot per pemanggilan; cache di level pemanggil."""
    g = Graph()
    g.parse(str(jalur), format="turtle")
    return g


def nama_lokal(term) -> str:
    """Localname dari sebuah IRI; literal dikembalikan apa adanya."""
    s = str(term)
    for pemisah in ("#", "/"):
        if pemisah in s:
            return s.rsplit(pemisah, 1)[-1]
    return s


def label(g: Graph, term, *, cadangan: bool = True) -> str:
    """`rdfs:label` kalau ada, kalau tidak balik ke nama lokal."""
    nilai = g.value(term, RDFS.label)
    if nilai is not None:
        return str(nilai)
    return nama_lokal(term) if cadangan else ""


def nilai_teks(nilai) -> str:
    """Tampilkan literal dengan bahasa Indonesia dan tanpa tanda kutip yang sia-sia."""
    if isinstance(nilai, bool):
        return "ya" if nilai else "tidak"
    return str(nilai)


def domain_penjelasan_awam(g: Graph) -> set:
    """Kelas yang sah menerima `penjelasanAwam`, dibaca dari axiom union di .ttl."""
    domain = g.value(NS.penjelasanAwam, RDFS.domain)
    if domain is None:
        return set()
    kepala = g.value(domain, OWL.unionOf)
    if kepala is None:
        return {domain}
    return {m for m in _koleksi(g, kepala) if m}


# --------------------------------------------------------------------------
# SWRL
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Atom:
    """Satu atom di `swrl:body` atau `swrl:head`."""

    jenis: str  # "kelas" | "objek" | "nilai" | "lain"
    predikat: URIRef | None
    argumen1: URIRef | None
    argumen2: object | None
    node: object  # blank node aslinya, untuk sitasi

    @classmethod
    def dari_node(cls, g: Graph, node) -> "Atom":
        tipe = g.value(node, RDF.type)
        predikat = g.value(node, SWRL.propertyPredicate) or g.value(node, SWRL.classPredicate)
        return cls(
            jenis={
                SWRL.ClassAtom: "kelas",
                SWRL.IndividualPropertyAtom: "objek",
                SWRL.DatavaluedPropertyAtom: "nilai",
            }.get(tipe, "lain"),
            predikat=predikat,
            argumen1=g.value(node, SWRL.argument1),
            argumen2=g.value(node, SWRL.argument2),
            node=node,
        )

    @property
    def nama_predikat(self) -> str:
        return nama_lokal(self.predikat) if self.predikat else "?"


@dataclass(frozen=True)
class Aturan:
    """Satu `swrl:Imp` beserta body dan head-nya."""

    iri: URIRef
    nama: str
    label: str
    comment: str
    body: tuple[Atom, ...]
    head: tuple[Atom, ...]


def _koleksi(g: Graph, node) -> list:
    """Baca RDF list (rdf:first / rdf:rest) menjadi list Python."""
    hasil: list = []
    dilalui: set = set()
    while node is not None and (node, RDF.first, None) in g:
        if node in dilalui:
            raise ValueError(f"lista RDF siklis di {nama_lokal(node)}")
        dilalui.add(node)
        hasil.append(g.value(node, RDF.first))
        node = g.value(node, RDF.rest)
    return hasil


def muat_aturan(g: Graph) -> dict[str, Aturan]:
    """Semua `swrl:Imp` di graph, diurut berdasarkan nama R1..Rn."""
    aturan: dict[str, Aturan] = {}
    for s in g.subjects(RDF.type, SWRL.Imp):
        body = _koleksi(g, g.value(s, SWRL.body))
        head = _koleksi(g, g.value(s, SWRL.head))
        aturan[nama_lokal(s)] = Aturan(
            iri=s,
            nama=nama_lokal(s),
            label=str(g.value(s, RDFS.label) or nama_lokal(s)),
            comment=str(g.value(s, RDFS.comment) or ""),
            body=tuple(Atom.dari_node(g, n) for n in body),
            head=tuple(Atom.dari_node(g, n) for n in head),
        )
    return dict(sorted(aturan.items()))


def variabel_kasus(g: Graph) -> URIRef:
    """IRI variabel yang slumpah ke kasus triase di `swrl:body`.

    Tidak di-hardcode ke satu namespace: ontology mendeklarasikan `:var_k`
    di namespace-nya sendiri dengan `rdfs:label "kasus"`, jadi kejar lewat
    deklarasi `a swrl:Variable` supaya tetap benar kalau prefix-nya berubah.
    """
    for v in sorted(g.subjects(RDF.type, SWRL.Variable), key=nama_lokal):
        if str(g.value(v, RDFS.label) or "") == "kasus":
            return v
    return VAR_KASUS


def slot_dari_aturan(aturan: Aturan, g: Graph) -> dict[str, Atom]:
    """Ambil slot yang harus diisi pengguna dari `swrl:body`.

    `swrl:body` adalah sumber kebenaran; daftar slot di `demo/app.py` dulu
    ditulis tangan dan bisa menyimpang dari ontology. Yang dikembalikan di
    sini setiap atom `DatavaluedPropertyAtom` yang menyebut var kasus, dengan
    nilai yang diharapkan dijawab pengguna (atau yang sudah jadi syarat).
    """
    var = variabel_kasus(g)
    slot: dict[str, Atom] = {}
    for atom in aturan.body:
        if atom.jenis != "nilai" or atom.predikat is None:
            continue
        if atom.argumen1 != var:
            continue
        slot[atom.nama_predikat] = atom
    return slot