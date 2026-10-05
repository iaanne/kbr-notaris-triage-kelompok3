# Aturan SWRL — versi manusia (parafrase orisinal)
Sumber pengetahuan: desk research UUJN No.2/2014, PP 24/2016 (PPAT),
KUHPerdata/KHI (waris), UU 42/1999 (fidusia), UU PT + Cipta Kerja (PT perorangan),
UU Perkawinan + Putusan MK 69/2015. Bukan salinan kalimat B-Team 3.

Format: JIKA (body) MAKA (head). Variabel ?k = kasus triase.

## R1 — Jual beli tanah bersertifikat yang sepakat → PPAT + AJB
JIKA KasusTriage(?k) ∧ punyaJenis(?k, jualBeli) ∧ punyaObjek(?k, tanahSHM)
     ∧ adaSertifikat(?k, true) ∧ adaSepakat(?k, true)
MAKA ditanganiOleh(?k, PPAT) ∧ butuhAkta(?k, AJB)

## R2 — Jual warisan tanpa SKW → belum lengkap + butuh SKW
JIKA KasusTriage(?k) ∧ punyaJenis(?k, warisJual) ∧ adaSKWaris(?k, false)
MAKA berstatus(?k, belumLengkap) ∧ butuhDokumen(?k, SKWaris)

## R3 — Waris tidak sepakat → rujuk pengadilan/mediasi
JIKA KasusTriage(?k) ∧ punyaJenis(?k, warisBagi) ∧ adaSepakat(?k, false)
MAKA ditanganiOleh(?k, Pengadilan) ∧ berstatus(?k, rujukPengadilan)

## R4 — Hibah tanah → PPAT + akta hibah + BPHTB
JIKA KasusTriage(?k) ∧ punyaJenis(?k, hibah) ∧ punyaObjek(?k, tanahSHM)
MAKA ditanganiOleh(?k, PPAT) ∧ butuhAkta(?k, aktaHibah) ∧ dikenaiBiaya(?k, BPHTB)

## R5 — Usaha 1 pendiri modal kecil → PT perorangan via AHU
JIKA KasusTriage(?k) ∧ punyaJenis(?k, dirikanUsaha)
     ∧ jumlahPendiri(?k, 1) ∧ modalKecil(?k, true)
MAKA butuhAkta(?k, PTperorangan) ∧ ditanganiOleh(?k, AHU)

## R6 — Utang jaminan kendaraan → notaris + fidusia
JIKA KasusTriage(?k) ∧ punyaJenis(?k, utangJaminan) ∧ punyaObjek(?k, kendaraan)
MAKA ditanganiOleh(?k, Notaris) ∧ butuhAkta(?k, fidusia)

## R7 — Wasiat cakap hukum → notaris + wasiat
JIKA KasusTriage(?k) ∧ punyaJenis(?k, wasiat) ∧ cakapHukum(?k, true)
MAKA ditanganiOleh(?k, Notaris) ∧ butuhAkta(?k, wasiat)
## R8 — Atur harta kawin sepakat → notaris + perjanjian kawin
JIKA KasusTriage(?k) ∧ punyaJenis(?k, kawinHarta) ∧ cakapHukum(?k, true)
     ∧ adaSepakat(?k, true)
MAKA ditanganiOleh(?k, Notaris) ∧ butuhAkta(?k, perjanjianKawin)

Versi mesin (SWRL RDF) ada di ontology/notaris-triage.ttl sebagai swrl:Imp
rule_R1..rule_R8 — bisa dibuka di Protege via tab SWRL.
Catatan: bila file di-save ulang dari Protege, body rule bisa terlepas
(Protege tidak round-trip swrl:Imp Turtle) — kembalikan dari git bila terjadi.
