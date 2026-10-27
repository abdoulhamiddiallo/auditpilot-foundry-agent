"""Moteur d'audit d'AuditPilot : le programme d'audit, codé une fois pour toutes.

Ce module applique exactement les sections 2 à 6 du Programme_Audit_Marches_BM : population auditée,
seuil de signification, sept tests d'analyse de données sur les marchés financés par la Banque mondiale
(loi de Benford, valeurs atypiques, doublons probables, fractionnement, gré à gré, concentration,
fournisseurs exclus), échantillon statistique par unités monétaires et cartographie des risques par pays.

Données réelles : contrats_marches_bm.csv (Banque mondiale, Finances One, jeu DS00005) et
sanctions_bm.csv (liste des entreprises et personnes exclues par la Banque mondiale), licence CC BY 4.0.

Utilisation dans l'interpréteur de code de l'agent :
    import glob
    exec(open(glob.glob("/mnt/data/*moteur_audit.py")[0]).read())
    r = calculer()                                     # périmètre officiel du programme
    afficher(r)                                        # tous les résultats, en français
    s = calculer(pays=["Guinée"])                      # périmètre restreint à un pays
    s = calculer(exclure=["1806694"])                  # simulation : contrat retiré de la population
    comparer(exclure=["1806694"])                      # simulation affichée avant · après, pays par pays
    fournisseur(r, "MOBISOFT")                         # contrats d'un fournisseur
    contrat(r, "1864571")                              # détail d'un contrat
    exporter_excel(r, "/mnt/data/audit_marches_BM.xlsx")

Utilisation locale, depuis la racine du dépôt :
    python agent/moteur_audit.py
"""
import difflib
import glob
import math
import os
import re
import unicodedata

import numpy as np
import pandas as pd

MATERIALITE_PCT = 0.5          # section 3 : seuil de signification, en % de la valeur de la population
REMONTEE_PCT = 5.0             # section 3 : seuil de remontée, en % du seuil de signification
BENFORD_SEUILS = (0.012, 0.015)  # section 4.1 : écart absolu moyen (MAD), conformité acceptable puis marginale
BENFORD_N_MIN = 1000           # section 4.1 : taille minimale de population
ATYPIQUE_Z = 4.5               # section 4.2 : score robuste au-delà duquel un montant est atypique
FRACTION_SEUIL, FRACTION_JOURS = 100_000, 30   # section 4.4
GRE_A_GRE_SEUILS = (20.0, 30.0)                # section 4.5 : part en valeur, en %
CONCENTRATION_SEUILS = (25.0, 40.0)            # section 4.6 : part du premier fournisseur, en %
SIMILARITE_NOM = 0.95                          # section 4.7 : similarité minimale de deux noms normalisés
FACTEUR_CONFIANCE = 3.0                        # section 5 : confiance de 95 %, aucune erreur attendue
STATUTS = ("RISQUE FAIBLE", "RISQUE MODÉRÉ", "RISQUE ÉLEVÉ")
PAYS_FR = {"Benin": "Bénin", "Burkina Faso": "Burkina Faso", "Cote d'Ivoire": "Côte d'Ivoire", "Guinea": "Guinée",
           "Guinea-Bissau": "Guinée-Bissau", "Mali": "Mali", "Niger": "Niger", "Senegal": "Sénégal", "Togo": "Togo"}
CATEGORIES_FR = {"Goods": "Fournitures", "Works": "Travaux", "Consultant Services": "Services de consultants",
                 "Non-consulting Services": "Services autres que de consultants"}
METHODES_FR = {"Request for Quotations": "Demande de cotations", "Individual Consultant Selection": "Sélection de consultant individuel",
               "Request for Bids": "Appel d'offres", "Direct Selection": "Gré à gré (sélection directe)",
               "Consultant Qualification  Selection": "Sélection fondée sur les qualifications",
               "Quality And Cost-Based Selection": "Sélection qualité-coût", "Quality Based Selection": "Sélection fondée sur la qualité",
               "Least Cost Selection": "Sélection au moindre coût", "Request for Proposals": "Demande de propositions",
               "UN Agencies (Direct)": "Agences des Nations unies", "Fixed Budget Selection": "Sélection à budget déterminé",
               "Non-Profit Organizations": "Organisations à but non lucratif", "Community Driven Development": "Développement communautaire"}
SUFFIXES = r"\b(SARL|SA|SAS|SASU|SUARL|LTD|LIMITED|LLC|INC|CO|COMPANY|CORP|CORPORATION|GROUP|GROUPE|ETS|ETABLISSEMENTS|" \
           r"ENTREPRISE|ENTREPRISES|SPRL|GMBH|AG|PLC|PVT|PRIVATE|BV|NV|SRL|SPA|SL|THE|ET|AND|DE|DU|DES|LA|LE|LES|M S|MS)\b"
CONSULTANT_ANONYME = "INDIVIDUAL CONSULTANT"


def _trouver(nom, essais=20, pause=3.0):
    """Retrouve un fichier, même renommé par Foundry (préfixe assistant-...), en patientant s'il n'est pas encore monté."""
    import time
    for k in range(essais):
        base, ext = os.path.splitext(nom)
        for motif in (f"/mnt/data/*{nom}", f"/mnt/data/**/*{nom}", f"/mnt/data/**/*{base}*{ext}", nom, f"*{nom}", f"../donnees/{nom}", f"donnees/{nom}"):
            trouves = glob.glob(motif, recursive=True)
            if trouves:
                return trouves[0]
        if k < essais - 1 and os.path.isdir("/mnt/data"):
            time.sleep(pause)
    raise FileNotFoundError(f"Fichier introuvable : {nom}. Le fichier n'est pas encore monté : relance la même cellule.")


def normaliser(nom):
    """Section 4.7 : nom en majuscules, sans accents, ponctuation, immatriculation ni forme juridique."""
    x = unicodedata.normalize("NFKD", str(nom)).encode("ascii", "ignore").decode().upper()
    x = re.sub(r"\(.*?\)", "", x)
    x = re.sub(r"[^A-Z0-9 ]", " ", x)
    x = re.sub(SUFFIXES, " ", x)
    return " ".join(x.split())


def statut_seuils(valeur, faible, eleve):
    """Statut à deux seuils : au-delà du second, risque élevé ; au-delà du premier, risque modéré."""
    if valeur > eleve:
        return STATUTS[2]
    if valeur > faible:
        return STATUTS[1]
    return STATUTS[0]


def statut_exposition(montant, materialite, remontee):
    """Section 3 : une exposition au moins égale au seuil de signification est un risque élevé."""
    if montant >= materialite:
        return STATUTS[2]
    if montant >= remontee:
        return STATUTS[1]
    return STATUTS[0]


def _benford(montants):
    m = montants[montants >= 10]
    chiffres = m.map(lambda v: int(f"{v:.6e}"[0]))
    obs = chiffres.value_counts(normalize=True).reindex(range(1, 10), fill_value=0.0).to_numpy()
    att = np.log10(1 + 1 / np.arange(1, 10))
    return len(m), float(np.abs(obs - att).mean()), obs, att


def calculer(pays=None, exercices=None, exclure=None):
    """Exécute tout le programme d'audit et renvoie un dictionnaire de résultats.

    pays : liste de pays emprunteurs (en français ou en anglais) pour restreindre le périmètre ;
    exercices : liste d'exercices de la Banque (2020 à 2026) ;
    exclure : liste de numéros de contrats Banque mondiale retirés de la population (simulation).
    """
    c = pd.read_csv(_trouver("contrats_marches_bm.csv"), dtype={"numero_contrat_bm": str, "id_fournisseur": str})
    s = pd.read_csv(_trouver("sanctions_bm.csv"))
    c["pays"] = c.pays_emprunteur.map(PAYS_FR).fillna(c.pays_emprunteur)
    if pays:
        cibles = {PAYS_FR.get(p, p) for p in pays}
        c = c[c.pays.isin(cibles)]
    if exercices:
        c = c[c.exercice_bm.isin(exercices)]
    if exclure:
        c = c[~c.numero_contrat_bm.isin([str(x) for x in exclure])]
    c = c.reset_index(drop=True)
    c["date"] = pd.to_datetime(c.date_signature)
    valeur = float(c.montant_usd.sum())
    materialite = valeur * MATERIALITE_PCT / 100
    remontee = materialite * REMONTEE_PCT / 100

    # Section 2 : population et qualité des données
    par_pays = c.groupby("pays").agg(contrats=("montant_usd", "size"), valeur=("montant_usd", "sum")).sort_values("valeur", ascending=False)
    par_exercice = c.groupby("exercice_bm").agg(contrats=("montant_usd", "size"), valeur=("montant_usd", "sum"))
    par_methode = c.groupby("methode_passation").agg(contrats=("montant_usd", "size"), valeur=("montant_usd", "sum")).sort_values("valeur", ascending=False)
    par_categorie = c.groupby("categorie").agg(contrats=("montant_usd", "size"), valeur=("montant_usd", "sum")).sort_values("valeur", ascending=False)
    qualite = {"montants_inferieurs_10_usd": int((c.montant_usd < 10).sum()), "fournisseur_manquant": int(c.fournisseur.isna().sum()),
               "type_revue_manquant": int(c.type_revue.isna().sum()), "consultants_anonymises": int((c.fournisseur == CONSULTANT_ANONYME).sum())}

    # Test 1 : loi de Benford (premier chiffre)
    n, mad, obs, att = _benford(c.montant_usd)
    benford = {"n": n, "mad": mad, "observe": obs, "attendu": att,
               "statut": statut_seuils(mad, *BENFORD_SEUILS) if n >= BENFORD_N_MIN else "NON APPLICABLE"}
    benford_pays = []
    for p, g in c.groupby("pays"):
        np_, madp, _, _ = _benford(g.montant_usd)
        benford_pays.append((p, np_, madp, statut_seuils(madp, *BENFORD_SEUILS) if np_ >= BENFORD_N_MIN else "NON APPLICABLE"))
    benford_pays = pd.DataFrame(benford_pays, columns=["pays", "montants", "mad", "statut"]).set_index("pays")

    # Test 2 : valeurs atypiques (score robuste sur le logarithme du montant, par catégorie)
    c["log"] = np.log10(c.montant_usd.clip(lower=1))
    z = pd.Series(0.0, index=c.index)
    for _, g in c.groupby("categorie"):
        med = g.log.median()
        mad_log = (g.log - med).abs().median() * 1.4826
        z[g.index] = (g.log - med) / mad_log
    c["score_robuste"] = z
    med_projet = c.groupby("id_projet").montant_usd.transform("median")
    c["multiple_mediane_projet"] = c.montant_usd / med_projet
    atypiques = c[c.score_robuste > ATYPIQUE_Z].sort_values("montant_usd", ascending=False)
    expo_atyp = float(atypiques.montant_usd.sum())

    # Test 3 : doublons probables (même fournisseur, même référence de l'emprunteur, même montant)
    cle = ["id_fournisseur", "reference_emprunteur", "montant_usd"]
    dbl = c[c.duplicated(cle, keep=False)].sort_values(cle + ["numero_contrat_bm"])
    excedent = float(dbl.montant_usd.sum() - dbl.drop_duplicates(cle).montant_usd.sum())
    groupes_doublons = dbl.groupby(cle, sort=False).agg(fournisseur=("fournisseur", "first"), pays=("pays", "first"),
                                                        enregistrements=("numero_contrat_bm", "size"),
                                                        contrats=("numero_contrat_bm", lambda x: " · ".join(x)),
                                                        methode=("methode_passation", "first")).reset_index()
    groupes_doublons["excedent"] = groupes_doublons.montant_usd * (groupes_doublons.enregistrements - 1)
    groupes_doublons = groupes_doublons.sort_values("excedent", ascending=False)

    # Test 4 : fractionnement (contrats sous le seuil, même fournisseur, projet et catégorie, à 30 jours d'intervalle au plus)
    grappes = []
    petits = c[c.montant_usd < FRACTION_SEUIL].sort_values(["date", "numero_contrat_bm"])
    for (fid, pid, cat), g in petits.groupby(["id_fournisseur", "id_projet", "categorie"]):
        if len(g) < 2:
            continue
        dates, montants, debut = g.date.to_numpy(), g.montant_usd.to_numpy(), 0
        for i in range(1, len(g) + 1):
            if i == len(g) or (dates[i] - dates[i - 1]) / np.timedelta64(1, "D") > FRACTION_JOURS:
                if i - debut >= 2 and montants[debut:i].sum() >= FRACTION_SEUIL:
                    grappes.append((g.fournisseur.iloc[0], g.pays.iloc[0], pid, CATEGORIES_FR.get(cat, cat), i - debut,
                                    float(montants[debut:i].sum()), str(g.date.iloc[debut].date()), str(g.date.iloc[i - 1].date())))
                debut = i
    grappes = pd.DataFrame(grappes, columns=["fournisseur", "pays", "id_projet", "categorie", "contrats", "total", "premier", "dernier"])
    grappes = grappes.sort_values("total", ascending=False).reset_index(drop=True)
    expo_frac = float(grappes.total.sum()) if len(grappes) else 0.0

    # Test 5 : gré à gré
    direct = c.methode_passation == "Direct Selection"
    part_gag = float(c[direct].montant_usd.sum() / valeur * 100)
    lignes_gag = {}
    for p, g in c.groupby("pays"):
        d = (g.methode_passation == "Direct Selection")
        lignes_gag[p] = {"contrats": int(d.sum()), "part_nombre": float(d.mean() * 100),
                         "part_valeur": float(g.loc[d, "montant_usd"].sum() / g.montant_usd.sum() * 100)}
    gag_pays = pd.DataFrame.from_dict(lignes_gag, orient="index")
    gag_pays.index.name = "pays"
    gag_pays["statut"] = gag_pays.part_valeur.map(lambda v: statut_seuils(v, *GRE_A_GRE_SEUILS))

    # Test 6 : concentration (premier fournisseur par pays, consultants individuels anonymisés exclus)
    conc = []
    for p, g in c[c.fournisseur != CONSULTANT_ANONYME].groupby("pays"):
        t = g.groupby("fournisseur").montant_usd.sum().sort_values(ascending=False)
        parts = t / t.sum()
        conc.append((p, t.index[0], float(t.iloc[0]), float(parts.iloc[0] * 100), float((parts ** 2).sum() * 10000)))
    conc = pd.DataFrame(conc, columns=["pays", "premier_fournisseur", "montant", "part", "hhi"]).set_index("pays")
    conc["statut"] = conc.part.map(lambda v: statut_seuils(v, *CONCENTRATION_SEUILS))

    # Test 7 : fournisseurs inscrits sur la liste d'exclusion de la Banque mondiale
    s["nom_normalise"] = s.nom.map(normaliser)
    index = {}
    for k, n_ in enumerate(s.nom_normalise):
        if n_:
            index.setdefault(n_.split()[0], []).append(k)
    correspondances = []
    for f in c.fournisseur.dropna().unique():
        if f == CONSULTANT_ANONYME:
            continue
        nf = normaliser(f)
        if len(nf) < 4:
            continue
        for k in index.get(nf.split()[0], []):
            ns = s.nom_normalise.iloc[k]
            sim = 1.0 if nf == ns else difflib.SequenceMatcher(None, nf, ns).ratio()
            if sim >= SIMILARITE_NOM:
                correspondances.append((f, k, sim))
    lignes = []
    for f, k, sim in correspondances:
        e = s.iloc[k]
        fin = pd.Timestamp("2100-12-31") if e.fin_exclusion in ("en cours", "permanente") else pd.Timestamp(e.fin_exclusion)
        debut = pd.Timestamp(e.debut_exclusion)
        for _, ct in c[c.fournisseur == f].iterrows():
            if debut <= ct.date <= fin:
                situation = "signé pendant l'exclusion"
            elif ct.date < debut:
                situation = "signé avant l'exclusion"
            else:
                situation = "signé après l'exclusion"
            lignes.append((ct.numero_contrat_bm, f, e.nom, e.pays, ct.pays, ct.date_signature, float(ct.montant_usd),
                           METHODES_FR.get(ct.methode_passation, ct.methode_passation), e.debut_exclusion, e.fin_exclusion, e.motif, situation, round(sim, 3)))
    sanctions = pd.DataFrame(lignes, columns=["numero_contrat_bm", "fournisseur", "nom_liste", "pays_liste", "pays", "date_signature", "montant_usd",
                                              "methode", "debut_exclusion", "fin_exclusion", "motif", "situation", "similarite"])
    sanctions = sanctions.drop_duplicates("numero_contrat_bm").sort_values("montant_usd", ascending=False).reset_index(drop=True)
    pendant = sanctions[sanctions.situation == "signé pendant l'exclusion"]
    if len(pendant):
        statut_sanctions = STATUTS[2]
    elif len(sanctions):
        statut_sanctions = STATUTS[1]
    else:
        statut_sanctions = STATUTS[0]

    # Section 5 : échantillon statistique par unités monétaires
    intervalle = materialite / FACTEUR_CONFIANCE
    taille = math.ceil(valeur / intervalle) if valeur else 0
    ordre = c.sort_values("numero_contrat_bm").reset_index(drop=True)
    cumul = ordre.montant_usd.cumsum().to_numpy()
    points = intervalle / 2 + intervalle * np.arange(taille)
    choisis = np.unique(np.searchsorted(cumul, points[points <= cumul[-1]], side="left")) if taille else np.array([], int)
    echantillon = ordre.iloc[choisis].copy()
    echantillon["element_cle"] = echantillon.montant_usd >= intervalle
    echantillon = echantillon.sort_values("montant_usd", ascending=False)

    # Section 6 : synthèse des tests
    tests = pd.DataFrame([
        ("Test 1 · Loi de Benford", f"écart absolu moyen {dec(benford['mad'], 4)} sur {benford['n']} montants", benford["statut"]),
        ("Test 2 · Valeurs atypiques", f"{len(atypiques)} contrats · {usd(expo_atyp)}", statut_exposition(expo_atyp, materialite, remontee)),
        ("Test 3 · Doublons probables", f"{len(groupes_doublons)} groupes · excédent {usd(excedent)}", statut_exposition(excedent, materialite, remontee)),
        ("Test 4 · Fractionnement", f"{len(grappes)} grappes · {usd(expo_frac)}", statut_exposition(expo_frac, materialite, remontee)),
        ("Test 5 · Gré à gré", f"{pct(part_gag)} de la valeur", statut_seuils(part_gag, *GRE_A_GRE_SEUILS)),
        ("Test 6 · Concentration", f"{int((conc.statut != STATUTS[0]).sum())} pays au-dessus de 25 %",
         STATUTS[2] if (conc.statut == STATUTS[2]).any() else (STATUTS[1] if (conc.statut == STATUTS[1]).any() else STATUTS[0])),
        ("Test 7 · Fournisseurs exclus", f"{len(sanctions)} contrats · {usd(float(sanctions.montant_usd.sum()) if len(sanctions) else 0.0)}", statut_sanctions),
    ], columns=["test", "resultat", "statut"])

    # Section 6 : cartographie des risques par pays
    rang = {STATUTS[0]: 0, STATUTS[1]: 1, STATUTS[2]: 2, "NON APPLICABLE": 0}
    carto = []
    for p in par_pays.index:
        sp = [benford_pays.statut.get(p, "NON APPLICABLE"), gag_pays.statut.get(p, STATUTS[0]), conc.statut.get(p, STATUTS[0])]
        exceptions = int((atypiques.pays == p).sum() + (groupes_doublons.pays == p).sum() + (grappes.pays == p).sum() + (sanctions.pays == p).sum())
        if (pendant.pays == p).any():
            sp.append(STATUTS[2])
        elif (sanctions.pays == p).any():
            sp.append(STATUTS[1])
        carto.append((p, int(par_pays.contrats[p]), float(par_pays.valeur[p]), sp[0], sp[1], sp[2], exceptions,
                      STATUTS[max(rang[x] for x in sp)]))
    carto = pd.DataFrame(carto, columns=["pays", "contrats", "valeur", "benford", "gre_a_gre", "concentration", "exceptions", "evaluation"]).set_index("pays")

    return {
        "contrats": c, "par_pays": par_pays, "par_exercice": par_exercice, "par_methode": par_methode, "par_categorie": par_categorie,
        "qualite": qualite, "benford": benford, "benford_pays": benford_pays, "atypiques": atypiques, "doublons": groupes_doublons,
        "fractionnement": grappes, "gre_a_gre_pays": gag_pays, "concentration": conc, "sanctions": sanctions, "echantillon": echantillon,
        "tests": tests, "cartographie": carto,
        "totaux": {"contrats": len(c), "valeur": valeur, "materialite": materialite, "remontee": remontee,
                   "fournisseurs": int(c.id_fournisseur.nunique()), "projets": int(c.id_projet.nunique()),
                   "exposition_atypiques": expo_atyp, "excedent_doublons": excedent, "exposition_fractionnement": expo_frac,
                   "part_gre_a_gre": part_gag, "exposition_sanctions": float(sanctions.montant_usd.sum()) if len(sanctions) else 0.0,
                   "intervalle_echantillon": intervalle, "taille_echantillon": len(echantillon),
                   "elements_cles": int(echantillon.element_cle.sum()), "valeur_echantillon": float(echantillon.montant_usd.sum()),
                   "simulation": bool(pays or exercices or exclure)},
    }


def usd(x):
    return ("- " if x < 0 else "") + f"{abs(x):,.0f} USD".replace(",", " ")


def pct(x):
    return f"{x:.2f} %".replace(".", ",")


def dec(x, n):
    return f"{x:.{n}f}".replace(".", ",")


def entier(x):
    return f"{x:,.0f}".replace(",", " ")


def contrat(r, numero):
    """Affiche le détail d'un contrat."""
    k = r["contrats"][r["contrats"].numero_contrat_bm == str(numero)]
    if k.empty:
        print(f"Contrat {numero} absent du périmètre.")
        return
    k = k.iloc[0]
    print(f"Contrat {k.numero_contrat_bm} · {k.pays} · exercice {k.exercice_bm} · signé le {k.date_signature}")
    print(f"Fournisseur {k.fournisseur} ({k.pays_fournisseur}) · {usd(k.montant_usd)}")
    print(f"{CATEGORIES_FR.get(k.categorie, k.categorie)} · {METHODES_FR.get(k.methode_passation, k.methode_passation)} · revue {k.type_revue}")
    print(f"Projet {k.id_projet} · {k.nom_projet}")
    print(f"Objet : {k.objet_du_contrat}")
    print(f"Score robuste {dec(k.score_robuste, 2)} · {entier(k.multiple_mediane_projet)} fois la médiane des contrats du projet")


def fournisseur(r, nom):
    """Affiche les contrats d'un fournisseur (recherche sur une partie du nom)."""
    c = r["contrats"][r["contrats"].fournisseur.str.contains(nom, case=False, na=False, regex=False)]
    print(f"{len(c)} contrats · {usd(c.montant_usd.sum())}")
    for _, k in c.sort_values("date").iterrows():
        print(f"{k.numero_contrat_bm} | {k.date_signature} | {k.pays} | {usd(k.montant_usd)} | {METHODES_FR.get(k.methode_passation, k.methode_passation)} | {k.reference_emprunteur}")


def comparer(pays=None, exercices=None, exclure=None):
    """Simulation : recalcule l'audit sur le périmètre demandé et affiche, pays par pays, chaque indicateur avant · après."""
    officiel = calculer()
    sim = calculer(pays=pays, exercices=exercices, exclure=exclure)
    perimetre = []
    if pays:
        perimetre.append("pays : " + ", ".join(pays))
    if exercices:
        perimetre.append("exercices : " + ", ".join(str(e) for e in exercices))
    if exclure:
        perimetre.append("contrats retirés : " + ", ".join(str(x) for x in exclure))
    print("SIMULATION (" + " · ".join(perimetre) + ") : les résultats officiels du programme ne changent pas (sections 2 et 8).")
    t0, t1 = officiel["totaux"], sim["totaux"]
    print(f"Population : {entier(t0['contrats'])} contrats · {usd(t0['valeur'])} avant · {entier(t1['contrats'])} contrats · {usd(t1['valeur'])} après")
    print("INDICATEUR | AVANT (OFFICIEL) | APRÈS (SIMULATION)")
    for _, l in sim["tests"].iterrows():
        a = officiel["tests"].set_index("test").loc[l.test]
        print(f"{l.test} | {a.resultat} · {a.statut} | {l.resultat} · {l.statut}")
    inchanges = []
    for p in sim["cartographie"].index:
        if (int(officiel["par_pays"].contrats[p]) == int(sim["par_pays"].contrats[p])
                and officiel["cartographie"].loc[p].evaluation == sim["cartographie"].loc[p].evaluation and len(sim["cartographie"]) > 1):
            inchanges.append(p)
            continue
        print(f"\nPAYS : {p}")
        print("INDICATEUR | AVANT (OFFICIEL) | APRÈS (SIMULATION)")
        g0, g1 = officiel["gre_a_gre_pays"].loc[p], sim["gre_a_gre_pays"].loc[p]
        print(f"Contrats | {entier(officiel['par_pays'].contrats[p])} · {usd(officiel['par_pays'].valeur[p])} | {entier(sim['par_pays'].contrats[p])} · {usd(sim['par_pays'].valeur[p])}")
        print(f"Gré à gré (test 5) | {pct(g0.part_valeur)} · {g0.statut} | {pct(g1.part_valeur)} · {g1.statut}")
        c0, c1 = officiel["concentration"].loc[p], sim["concentration"].loc[p]
        print(f"Concentration (test 6) | {c0.premier_fournisseur} · {usd(c0.montant)} · {pct(c0.part)} · {c0.statut} | "
              f"{c1.premier_fournisseur} · {usd(c1.montant)} · {pct(c1.part)} · {c1.statut}")
        k0, k1 = officiel["cartographie"].loc[p], sim["cartographie"].loc[p]
        print(f"Évaluation d'ensemble (section 6) | {k0.evaluation} | {k1.evaluation}")
    if inchanges:
        print("\nPays inchangés par la simulation : " + ", ".join(inchanges))
    return sim


def afficher(r):
    """Affiche le rapport d'audit analytique au format du programme."""
    t = r["totaux"]
    if t["simulation"]:
        print("PÉRIMÈTRE DE SIMULATION : les résultats officiels du programme ne changent pas.\n")
    print("POPULATION AUDITÉE (section 2) : contrats financés par la Banque mondiale, exercices 2020 à 2026")
    print(f"{t['contrats']} contrats · {usd(t['valeur'])} · {t['fournisseurs']} fournisseurs · {t['projets']} projets")
    print("PAYS | CONTRATS | VALEUR | PART")
    for p, l in r["par_pays"].iterrows():
        print(f"{p} | {int(l.contrats)} | {usd(l.valeur)} | {pct(l.valeur / t['valeur'] * 100)}")
    q = r["qualite"]
    print(f"Qualité des données : {q['montants_inferieurs_10_usd']} montants inférieurs à 10 USD · {q['type_revue_manquant']} types de revue manquants · "
          f"{q['consultants_anonymises']} consultants individuels anonymisés par la source")
    print(f"\nSEUIL DE SIGNIFICATION (section 3) : {usd(t['materialite'])} · seuil de remontée : {usd(t['remontee'])}")

    b = r["benford"]
    print(f"\nTEST 1 · LOI DE BENFORD (section 4.1) : {b['n']} montants · écart absolu moyen {dec(b['mad'], 4)} · {b['statut']}")
    print("CHIFFRE | OBSERVÉ | ATTENDU")
    for d in range(9):
        print(f"{d + 1} | {pct(b['observe'][d] * 100)} | {pct(b['attendu'][d] * 100)}")
    print("PAYS | MONTANTS | ÉCART ABSOLU MOYEN | STATUT")
    for p, l in r["benford_pays"].iterrows():
        print(f"{p} | {l.montants} | {dec(l['mad'], 4)} | {l.statut}")

    print(f"\nTEST 2 · VALEURS ATYPIQUES (section 4.2) : {len(r['atypiques'])} contrats · {usd(t['exposition_atypiques'])}")
    print("CONTRAT | PAYS | FOURNISSEUR | MONTANT | SCORE ROBUSTE | MULTIPLE DE LA MÉDIANE DU PROJET | OBJET")
    for _, k in r["atypiques"].iterrows():
        print(f"{k.numero_contrat_bm} | {k.pays} | {k.fournisseur} | {usd(k.montant_usd)} | {dec(k.score_robuste, 2)} | "
              f"{entier(k.multiple_mediane_projet)} | {k.objet_du_contrat[:90]}")

    d = r["doublons"]
    print(f"\nTEST 3 · DOUBLONS PROBABLES (section 4.3) : {len(d)} groupes · {int(d.enregistrements.sum()) if len(d) else 0} enregistrements · excédent {usd(t['excedent_doublons'])}")
    print("FOURNISSEUR | PAYS | RÉFÉRENCE DE L'EMPRUNTEUR | MONTANT UNITAIRE | ENREGISTREMENTS | CONTRATS | EXCÉDENT")
    for _, k in d.head(10).iterrows():
        print(f"{k.fournisseur} | {k.pays} | {k.reference_emprunteur} | {usd(k.montant_usd)} | {k.enregistrements} | {k.contrats} | {usd(k.excedent)}")

    g = r["fractionnement"]
    print(f"\nTEST 4 · FRACTIONNEMENT (section 4.4) : {len(g)} grappes · {int(g.contrats.sum()) if len(g) else 0} contrats · {usd(t['exposition_fractionnement'])}")
    print("FOURNISSEUR | PAYS | PROJET | CATÉGORIE | CONTRATS | TOTAL | DU | AU")
    for _, k in g.head(10).iterrows():
        print(f"{k.fournisseur} | {k.pays} | {k.id_projet} | {k.categorie} | {k.contrats} | {usd(k.total)} | {k.premier} | {k.dernier}")

    print(f"\nTEST 5 · GRÉ À GRÉ (section 4.5) : {pct(t['part_gre_a_gre'])} de la valeur totale")
    print("PAYS | CONTRATS DE GRÉ À GRÉ | PART EN NOMBRE | PART EN VALEUR | STATUT")
    for p, l in r["gre_a_gre_pays"].sort_values("part_valeur", ascending=False).iterrows():
        print(f"{p} | {int(l.contrats)} | {pct(l.part_nombre)} | {pct(l.part_valeur)} | {l.statut}")

    ge = r["gre_a_gre_pays"].sort_values("part_valeur", ascending=False)
    for st in (STATUTS[2], STATUTS[1]):
        sel = ge[ge.statut == st]
        print(f"Pays en {st} pour le gré à gré (test 5) : " + (" · ".join(f"{p} {pct(v)}" for p, v in sel.part_valeur.items()) if len(sel) else "aucun"))

    print("\nTEST 6 · CONCENTRATION DES FOURNISSEURS (section 4.6)")
    print("PAYS | PREMIER FOURNISSEUR | MONTANT | PART | INDICE DE HERFINDAHL | STATUT")
    for p, l in r["concentration"].sort_values("part", ascending=False).iterrows():
        print(f"{p} | {l.premier_fournisseur} | {usd(l.montant)} | {pct(l.part)} | {int(round(l.hhi))} | {l.statut}")

    co = r["concentration"].sort_values("part", ascending=False)
    for st in (STATUTS[2], STATUTS[1]):
        sel = co[co.statut == st]
        print(f"Pays en {st} pour la concentration (test 6) : " + (" · ".join(f"{p} {pct(v)}" for p, v in sel.part.items()) if len(sel) else "aucun"))

    s = r["sanctions"]
    print(f"\nTEST 7 · FOURNISSEURS EXCLUS PAR LA BANQUE MONDIALE (section 4.7) : {len(s)} contrats · {usd(t['exposition_sanctions'])}")
    print("CONTRAT | FOURNISSEUR | PAYS | SIGNÉ LE | MONTANT | EXCLUSION | MOTIF | SITUATION")
    for _, k in s.iterrows():
        print(f"{k.numero_contrat_bm} | {k.fournisseur} | {k.pays} | {k.date_signature} | {usd(k.montant_usd)} | du {k.debut_exclusion} au {k.fin_exclusion} | {k.motif} | {k.situation}")

    e = r["echantillon"]
    print(f"\nÉCHANTILLON STATISTIQUE PAR UNITÉS MONÉTAIRES (section 5) : intervalle {usd(t['intervalle_echantillon'])} · "
          f"{t['taille_echantillon']} contrats · {t['elements_cles']} éléments clés · {usd(t['valeur_echantillon'])} couverts "
          f"({pct(t['valeur_echantillon'] / t['valeur'] * 100)} de la valeur)")

    print("\nCARTOGRAPHIE DES RISQUES PAR PAYS (section 6) : évaluation d'ensemble de chaque pays, tous tests confondus. Pour les pays en risque d'un test donné, utilise la ligne de ce test.")
    print("PAYS | CONTRATS | VALEUR | BENFORD | GRÉ À GRÉ | CONCENTRATION | EXCEPTIONS | ÉVALUATION")
    for p, l in r["cartographie"].iterrows():
        print(f"{p} | {l.contrats} | {usd(l.valeur)} | {l.benford} | {l.gre_a_gre} | {l.concentration} | {l.exceptions} | {l.evaluation}")

    print("\nSYNTHÈSE DES TESTS (section 6)")
    print("TEST | RÉSULTAT | STATUT")
    for _, l in r["tests"].iterrows():
        print(f"{l.test} | {l.resultat} | {l.statut}")
    print("\nSUITES À DONNER (section 7)")
    suites = {
        "Test 1 · Loi de Benford": "Benford : analyse des deux premiers chiffres et revue des montants qui créent l'écart dans les pays concernés.",
        "Test 2 · Valeurs atypiques": "Valeurs atypiques : corroboration de chaque montant avec le contrat signé et la devise d'origine avant toute conclusion.",
        "Test 3 · Doublons probables": "Doublons : rapprochement avec les paiements effectifs et confirmation écrite de l'agence d'exécution sous 30 jours.",
        "Test 4 · Fractionnement": "Fractionnement : revue du plan de passation des marchés et des seuils applicables pour chaque grappe.",
        "Test 5 · Gré à gré": "Gré à gré : contrôle des justifications de sélection directe sur un échantillon par pays concerné.",
        "Test 6 · Concentration": "Concentration : revue des conditions de concurrence des marchés du premier fournisseur.",
        "Test 7 · Fournisseurs exclus": "Fournisseurs exclus : revue rétrospective des contrats concernés et information de la vice-présidence Intégrité de la Banque mondiale si un contrat est signé pendant l'exclusion.",
    }
    k = 0
    for _, l in r["tests"].iterrows():
        if l.statut in (STATUTS[1], STATUTS[2]):
            k += 1
            print(f"{k}. {suites[l.test]} ({l.statut})")
    print("Un constat analytique signale un risque à examiner : il ne constitue ni une preuve de fraude ni une accusation (section 8).")


def exporter_excel(r, chemin="/mnt/data/audit_marches_BM.xlsx"):
    """Écrit le classeur de travail de l'auditeur : synthèse, exceptions de chaque test, échantillon."""
    colonnes = ["numero_contrat_bm", "pays", "exercice_bm", "date_signature", "fournisseur", "montant_usd", "categorie", "methode_passation",
                "id_projet", "reference_emprunteur", "objet_du_contrat"]
    with pd.ExcelWriter(chemin) as classeur:
        r["tests"].to_excel(classeur, sheet_name="Synthèse", index=False)
        r["cartographie"].reset_index().to_excel(classeur, sheet_name="Cartographie", index=False)
        r["benford_pays"].reset_index().to_excel(classeur, sheet_name="Benford", index=False)
        r["atypiques"][colonnes + ["score_robuste", "multiple_mediane_projet"]].to_excel(classeur, sheet_name="Valeurs atypiques", index=False)
        r["doublons"].to_excel(classeur, sheet_name="Doublons", index=False)
        r["fractionnement"].to_excel(classeur, sheet_name="Fractionnement", index=False)
        r["gre_a_gre_pays"].reset_index().to_excel(classeur, sheet_name="Gré à gré", index=False)
        r["concentration"].reset_index().to_excel(classeur, sheet_name="Concentration", index=False)
        r["sanctions"].to_excel(classeur, sheet_name="Fournisseurs exclus", index=False)
        r["echantillon"][colonnes + ["element_cle"]].to_excel(classeur, sheet_name="Échantillon", index=False)
    return chemin


if __name__ == "__main__" and globals().get("__file__", "").endswith("moteur_audit.py"):
    ici = os.path.dirname(os.path.abspath(__file__))
    donnees = os.path.join(ici, "..", "donnees")
    os.chdir(donnees if os.path.isdir(donnees) and not os.path.exists(os.path.join(ici, "contrats_marches_bm.csv")) else ici)
    afficher(calculer())
