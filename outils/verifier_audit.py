"""Recalcule les tests du programme d'audit sans AI, puis les compare au moteur de l'agent.

Ce script est une seconde implémentation, écrite indépendamment du moteur agent/moteur_audit.py,
des sections 2 à 5 du programme d'audit : population, seuil de signification, loi de Benford, doublons
probables, fractionnement, gré à gré, concentration, fournisseurs exclus et taille de l'échantillon.
Il utilise le module csv et des boucles explicites plutôt que les regroupements de pandas, produit les
réponses de référence de l'évaluation, puis vérifie que le moteur donne exactement les mêmes résultats.

Utilisation, depuis la racine du dépôt :
    pip install -r outils/requirements.txt
    python outils/verifier_audit.py
"""
import csv
import difflib
import math
import os
import re
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DONNEES = RACINE / "donnees"
if not (DONNEES / "contrats_marches_bm.csv").exists():
    DONNEES = Path(__file__).resolve().parent.parent / "donnees"


def usd(x):
    return f"{x:,.0f} USD".replace(",", " ")


def lire(nom):
    with open(DONNEES / nom, encoding="utf-8") as f:
        return list(csv.DictReader(f))


contrats = lire("contrats_marches_bm.csv")
exclus = lire("sanctions_bm.csv")
for k in contrats:
    k["m"] = float(k["montant_usd"])
    k["d"] = date.fromisoformat(k["date_signature"])

valeur = sum(k["m"] for k in contrats)
materialite = valeur * 0.005
remontee = materialite * 0.05

# Loi de Benford : premier chiffre significatif des montants d'au moins 10 USD
compte = [0] * 10
for k in contrats:
    if k["m"] >= 10:
        compte[int(k["m"] / 10 ** math.floor(math.log10(k["m"])))] += 1
n_benford = sum(compte)
mad = sum(abs(compte[d] / n_benford - math.log10(1 + 1 / d)) for d in range(1, 10)) / 9

# Doublons probables : même fournisseur, même référence de l'emprunteur, même montant
groupes = defaultdict(list)
for k in contrats:
    groupes[(k["id_fournisseur"], k["reference_emprunteur"], k["montant_usd"])].append(k)
doublons = {g: v for g, v in groupes.items() if len(v) > 1}
excedent = sum(v[0]["m"] * (len(v) - 1) for v in doublons.values())

# Fractionnement : contrats de moins de 100 000 USD, enchaînés à 30 jours au plus
paquets = defaultdict(list)
for k in contrats:
    if k["m"] < 100_000:
        paquets[(k["id_fournisseur"], k["id_projet"], k["categorie"])].append(k)
grappes, expo_frac = 0, 0.0
for v in paquets.values():
    v.sort(key=lambda k: (k["d"], k["numero_contrat_bm"]))
    chaine = [v[0]]
    for k in v[1:] + [None]:
        if k is not None and (k["d"] - chaine[-1]["d"]).days <= 30:
            chaine.append(k)
            continue
        total = sum(x["m"] for x in chaine)
        if len(chaine) >= 2 and total >= 100_000:
            grappes += 1
            expo_frac += total
        chaine = [k] if k is not None else []

# Gré à gré et concentration
part_gag = sum(k["m"] for k in contrats if k["methode_passation"] == "Direct Selection") / valeur * 100
par_pays = defaultdict(lambda: defaultdict(float))
for k in contrats:
    if k["fournisseur"] != "INDIVIDUAL CONSULTANT":
        par_pays[k["pays_emprunteur"]][k["fournisseur"]] += k["m"]
concentration = {p: max(f.values()) / sum(f.values()) * 100 for p, f in par_pays.items()}

# Fournisseurs exclus : noms normalisés identiques ou similaires à 95 % au moins
FORMES = {"SARL", "SA", "SAS", "SASU", "SUARL", "LTD", "LIMITED", "LLC", "INC", "CO", "COMPANY", "CORP", "CORPORATION", "GROUP", "GROUPE",
          "ETS", "ETABLISSEMENTS", "ENTREPRISE", "ENTREPRISES", "SPRL", "GMBH", "AG", "PLC", "PVT", "PRIVATE", "BV", "NV", "SRL", "SPA",
          "SL", "THE", "ET", "AND", "DE", "DU", "DES", "LA", "LE", "LES", "MS"}


def normaliser(nom):
    x = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode().upper()
    x = re.sub(r"\(.*?\)", "", x)
    x = re.sub(r"[^A-Z0-9 ]", " ", x)
    x = re.sub(r"\bM S\b", " ", x)
    return " ".join(m for m in x.split() if m not in FORMES)


noms_exclus = [(normaliser(e["nom"]), e) for e in exclus]
contrats_exclus = {}
for k in contrats:
    if k["fournisseur"] == "INDIVIDUAL CONSULTANT":
        continue
    nf = normaliser(k["fournisseur"])
    if len(nf) < 4:
        continue
    for ne, e in noms_exclus:
        if ne and ne.split()[0] == nf.split()[0] and (ne == nf or difflib.SequenceMatcher(None, nf, ne).ratio() >= 0.95):
            contrats_exclus[k["numero_contrat_bm"]] = k
expo_exclus = sum(k["m"] for k in contrats_exclus.values())

intervalle = materialite / 3.0
taille_theorique = math.ceil(valeur / intervalle)

print("=" * 78)
print("AUDIT DES MARCHÉS FINANCÉS PAR LA BANQUE MONDIALE · UEMOA ET GUINÉE · EXERCICES 2020 À 2026")
print("=" * 78)
print(f"{len(contrats)} contrats · {usd(valeur)} · seuil de signification {usd(materialite)}")
print(f"Benford : écart absolu moyen {mad:.4f} sur {n_benford} montants".replace(".", ","))
print(f"Doublons probables : {len(doublons)} groupes · excédent {usd(excedent)}")
print(f"Fractionnement : {grappes} grappes · {usd(expo_frac)}")
print(f"Gré à gré : {part_gag:.2f} % de la valeur".replace(".", ","))
print(f"Fournisseurs exclus : {len(contrats_exclus)} contrats · {usd(expo_exclus)}")
print(f"Échantillon par unités monétaires : intervalle {usd(intervalle)} · {taille_theorique} points de sélection")

print("\nCONTRÔLE CROISÉ AVEC agent/moteur_audit.py")
os.chdir(DONNEES)
moteur = {}
exec((RACINE / "agent" / "moteur_audit.py").read_text(encoding="utf-8") if (RACINE / "agent" / "moteur_audit.py").exists()
     else (DONNEES / "moteur_audit.py").read_text(encoding="utf-8"), moteur)
r = moteur["calculer"]()
t = r["totaux"]
paires = {
    "Nombre de contrats": (t["contrats"], len(contrats)),
    "Valeur de la population": (t["valeur"], valeur),
    "Seuil de signification": (t["materialite"], materialite),
    "Benford : MAD × 1 000 000": (r["benford"]["mad"] * 1e6, mad * 1e6),
    "Excédent des doublons": (t["excedent_doublons"], excedent),
    "Grappes de fractionnement": (len(r["fractionnement"]), grappes),
    "Exposition au fractionnement": (t["exposition_fractionnement"], expo_frac),
    "Gré à gré : part × 10 000": (t["part_gre_a_gre"] * 100, part_gag * 100),
    "Contrats de fournisseurs exclus": (len(r["sanctions"]), len(contrats_exclus)),
    "Exposition aux fournisseurs exclus": (t["exposition_sanctions"], expo_exclus),
    "Concentration Guinée-Bissau × 100": (r["concentration"].part["Guinée-Bissau"] * 100, concentration["Guinea-Bissau"] * 100),
}
ecarts = {nom: abs(round(a) - round(b)) for nom, (a, b) in paires.items()}
for nom, e in ecarts.items():
    print(f"  {'✓' if e == 0 else '✗'} {nom:<36} {round(paires[nom][1]):>16,}   écart {e}".replace(",", " "))
print(f"\n{sum(e == 0 for e in ecarts.values())} indicateurs sur {len(ecarts)} identiques.")
