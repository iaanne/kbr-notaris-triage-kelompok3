"""Lapisan baca-tulis di atas ontology Notaris Triage.

Pola proyek ini: fakta selalu datang dari ontology, tidak pernah dari teks
karangan. Modul ini dipakai bersama oleh demo/, notaris/, dan eval/.
"""

from pathlib import Path

#: Akar repo, satu tingkat di atas paket ini.
AKAR = Path(__file__).resolve().parent.parent

#: Ontology OWL DL sumber tunggal.
TTL = AKAR / "ontology" / "notaris-triage.ttl"

#: Berkas hasil generate. Turunan, bukan sumber kebenaran.
DATA = AKAR / "data"

__all__ = ["AKAR", "TTL", "DATA"]