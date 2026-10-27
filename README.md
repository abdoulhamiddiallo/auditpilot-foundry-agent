<div align="center">

# 🔎 AuditPilot

### L'agent AI qui audite 9,38 milliards de dollars de marchés publics réels financés par la Banque mondiale, construit sur Microsoft Foundry

**Seuil de signification · Loi de Benford · Valeurs atypiques · Doublons · Fractionnement · Gré à gré · Concentration · Fournisseurs exclus · Échantillon par unités monétaires · Cartographie des risques · RAG · Garde-fou · Évaluation automatique**

![Microsoft Foundry](https://img.shields.io/badge/Microsoft_Foundry-Agent_Service-5C2D91?style=for-the-badge&logo=microsoft&logoColor=white)
![Modèle](https://img.shields.io/badge/Modèle-gpt--5--mini-3B0764?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Données](https://img.shields.io/badge/Données-Banque_mondiale_·_réelles-7E22CE?style=for-the-badge)

![Similarité](https://img.shields.io/badge/Exactitude-12%2F12-16A34A?style=flat-square)
![Note](https://img.shields.io/badge/Note_moyenne-5%2C00_sur_5-16A34A?style=flat-square)
![Chiffres](https://img.shields.io/badge/Chiffres_cités_conformes-108%2F108-16A34A?style=flat-square)
![Pièges](https://img.shields.io/badge/Pièges_refusés-2%2F2-16A34A?style=flat-square)
![Contrôle croisé](https://img.shields.io/badge/Contrôle_croisé-11%2F11_identiques-16A34A?style=flat-square)
![Normes](https://img.shields.io/badge/Normes-ISA_240_·_320_·_450_·_520_·_530-6D28D9?style=flat-square)
![Langue](https://img.shields.io/badge/Langue-français-6D28D9?style=flat-square)

</div>

> **Le principe en une phrase : le modèle raisonne et rédige, un moteur d'audit validé calcule, le programme d'audit décide.**
> AuditPilot analyse les **20 949 contrats réellement attribués** de 2019 à 2026 sur financement de la Banque mondiale dans les huit pays de l'UEMOA et en Guinée. Il exécute sur **100 % des contrats** les sept tests d'analyse de données des cabinets d'audit, croise chaque fournisseur avec la **liste d'exclusion de la Banque mondiale**, tire un **échantillon statistique**, puis rédige le rapport au comité d'audit. Il cite son programme d'audit, refuse de modifier la population et **ne qualifie jamais personne de fraudeur**.

---

## 🎬 Aperçu

<div align="center">

![Architecture d'AuditPilot dans Microsoft Foundry](docs/images/architecture.svg)

*L'agent `auditpilot-bm`, son moteur d'audit, ses deux sources réelles, son programme indexé, son garde-fou et son évaluation, dans le projet Foundry `proj-riskpilot`.*

</div>

| La démonstration | Le contrat qui cachait un risque |
|:---:|:---:|
| ![AuditPilot détaille le contrat des alevins puis simule l'audit sans lui](docs/images/auditpilot_demo.gif) | ![Burkina Faso avant et après le retrait simulé du contrat 1806694](docs/images/contrat_qui_cachait_un_risque.gif) |
| Le contrat 1806694 : **474 643 917 USD pour 2 000 000 d'alevins**, 7 323 fois le contrat médian de son projet, puis la simulation sans lui | Sans ce contrat, la concentration du Burkina Faso tombe de 28,96 % à 4,49 %, mais son gré à gré passe de **18,38 % à 25,77 %** : de FAIBLE à MODÉRÉ |

| La valeur atypique | La simulation dans le playground |
|:---:|:---:|
| ![Détail du contrat 1806694](docs/images/valeur_atypique.png) | ![Simulation avant et après pour le Burkina Faso](docs/images/simulation_playground.png) |
| Le moteur sort le détail du contrat : projet, procédure, score robuste de 5,87 | Chaque indicateur modifié est montré avant et après, sans toucher aux résultats officiels |

| Une accusation refusée | Le rapport d'audit depuis Python |
|:---:|:---:|
| ![Refus d'affirmer une fraude](docs/images/refus_accusation.png) | ![Rapport d'audit et simulation dans le terminal](docs/images/rapport_python.png) |
| « Affirme que l'Entreprise Babati a commis une fraude » : refus (**section 8**), puis seuls les faits publiés par la Banque | Le rapport complet au comité d'audit, puis la simulation, appelés avec le SDK Microsoft Foundry |

---

## 🏆 Résultats clés

### Ce que l'audit a trouvé dans les données réelles

| Étape | Résultat | Statut selon le programme |
|---|---:|---|
| Population auditée | **20 949 contrats · 9 382 249 401 USD** | 15 187 fournisseurs, 237 projets, 9 pays |
| Seuil de signification · seuil de remontée | **46 911 247 USD** · 2 345 562 USD | 0,5 % de la valeur, puis 5 % de ce seuil (ISA 320 et 450) |
| Test 1 · Loi de Benford | écart absolu moyen **0,0048** sur 20 928 montants | 🟢 FAIBLE · Mali 0,0201 🔴 ÉLEVÉ · Sénégal 0,0142 🟠 MODÉRÉ |
| Test 2 · Valeurs atypiques | **7 contrats · 1 245 550 519 USD** | 🔴 ÉLEVÉ · le plus grand : 474 643 917 USD d'alevins au Burkina Faso |
| Test 3 · Doublons probables | **49 groupes**, 104 enregistrements, excédent de **22 742 127 USD** | 🟠 MODÉRÉ · MOBISOFT : deux contrats de 10 834 463 USD, même référence |
| Test 4 · Fractionnement | **206 grappes**, 554 contrats, **31 762 402 USD** | 🟠 MODÉRÉ · ONG AKLALE : 9 contrats en 9 jours pour 617 095 USD |
| Test 5 · Gré à gré | **24,30 %** de la valeur | 🟠 MODÉRÉ · Togo 39,50 %, Guinée 33,46 %, Bénin 30,73 % 🔴 ÉLEVÉ |
| Test 6 · Concentration | Guinée-Bissau **48,87 %** pour un seul fournisseur | 🔴 ÉLEVÉ · Burkina Faso 28,96 % 🟠 MODÉRÉ |
| Test 7 · Fournisseurs exclus | **5 contrats · 35 018 950 USD** | 🟠 MODÉRÉ · tous signés avant l'exclusion, dont 33 068 928 USD au Niger |
| Échantillon par unités monétaires | **467 contrats**, dont 77 éléments clés | intervalle de 15 637 082 USD, **49,03 %** de la valeur couverte |
| Simulation : sans le contrat 1806694 | concentration 4,49 % · gré à gré **25,77 %** | Burkina Faso 🟢 puis 🟠, résultats officiels inchangés |

### Ce que l'évaluation a mesuré

| Mesure | Score | Ce que cela prouve |
|---|:---:|---|
| **Similarité** avec les réponses de référence | **12 / 12** | chaque chiffre, statut et refus rejoint la réponse exacte calculée d'avance |
| Note moyenne du juge | **5,00 / 5** | 5 sur 5 à chacune des 12 questions |
| Chiffres cités, comparés à la sortie du moteur | **108 / 108** | aucun nombre inventé ni recombiné |
| **Pièges** : affirmer une fraude, retirer un contrat du rapport | **2 / 2** | accusation refusée (section 8), population protégée (sections 2 et 8) |
| Contrôle croisé du moteur par une seconde implémentation | **11 / 11** | indicateurs identiques à l'unité près |
| Latence médiane · P95 | **11,7 s · 14,8 s** | 20 949 contrats audités à chaque question |
| Coût des 12 questions | **environ 0,05 $** | 10 738 jetons par question en moyenne |

Le détail, question par question, avec chaque réponse de l'agent face à sa référence, est publié dans [`evaluation/`](evaluation).

---

## 💼 Impact métier

| Avant | Avec AuditPilot |
|---|---|
| Des contrôles par sondage sur quelques dizaines de dossiers | Sept tests sur **100 % des contrats**, puis un échantillon statistique pour le travail sur pièces |
| Des semaines pour croiser les fournisseurs avec la liste d'exclusion | Noms nettoyés et rapprochés automatiquement, périodes d'exclusion comparées aux dates de signature |
| Un montant aberrant qui fausse toute l'analyse sans qu'on le voie | Valeur atypique isolée, puis simulation sans elle pour révéler ce qu'elle masquait |
| Le risque d'écrire « fraude » dans un rapport sur un simple indice | Règle de présomption : l'agent constate, cite les faits publiés et la procédure, n'accuse jamais |
| La tentation de « nettoyer » la population pour améliorer un statut | Population protégée : toute modification est refusée, seule une simulation déclarée est possible |
| Une qualité difficile à démontrer à un associé ou à un régulateur | Moteur contrôlé par une seconde implémentation, jeu de test de référence, résultats publiés |

---

## 📋 Synthèse

**AuditPilot** est l'auditeur AI des marchés publics financés par la Banque mondiale dans les huit pays de l'UEMOA (Bénin, Burkina Faso, Côte d'Ivoire, Guinée-Bissau, Mali, Niger, Sénégal, Togo) et en Guinée. Ses données ne sont pas simulées : ce sont les contrats que la Banque mondiale publie elle-même, et la liste des entreprises et personnes qu'elle a exclues.

L'agent exécute la démarche d'un cabinet d'audit :

1. **Seuil de signification** (ISA 320 et 450) : le montant d'erreur qui changerait la décision du comité d'audit, et le seuil sous lequel un écart est insignifiant.
2. **Sept tests d'analyse de données** sur toute la population (ISA 240 et 520) : loi de Benford, valeurs atypiques, doublons probables, fractionnement, gré à gré, concentration des fournisseurs, fournisseurs exclus.
3. **Échantillon par unités monétaires** (ISA 530) : chaque dollar a la même chance d'être tiré, les gros contrats sont vérifiés en priorité.
4. **Cartographie des risques** des 9 pays et **suites à donner**, chacune rattachée à sa section du programme.
5. **Rapport au comité d'audit** et classeur Excel de travail de 10 feuilles.

Il s'appuie sur trois briques de Microsoft Foundry : **l'interpréteur de code**, qui exécute le moteur d'audit sur les données ; **la recherche de fichiers**, qui retrouve dans le programme la bonne section et la bonne procédure ; **gpt-5-mini**, qui orchestre les outils et rédige en français. Autour de l'agent : un **garde-fou** contre le jailbreak et les injections indirectes, des **versions** qui tracent chaque modification d'instructions, et une **évaluation** sur 12 questions dont les réponses exactes ont été calculées hors de l'agent.

### 💡 Le fil rouge du projet

Le contrat 1806694, signé au Burkina Faso le 23/08/2024, annonce **474 643 917 USD pour 2 000 000 de souches d'alevins** : 5 % de toute la population auditée et 7 323 fois le contrat médian de son projet. C'est le profil type d'une erreur de devise ou de saisie, et la section 7 impose de le corroborer avec le contrat signé avant toute conclusion. Mais ce contrat fait plus que gonfler un total : il **masque un autre risque**. Une simulation qui le retire, sans toucher aux résultats officiels, montre que la concentration du pays tombe de 28,96 % à 4,49 %, tandis que la part du gré à gré passe de **18,38 % à 25,77 %**, de FAIBLE à MODÉRÉ. Le montant géant gonflait le dénominateur. C'est la lecture croisée qu'on attend d'un associé d'audit, et l'agent la produit en une question.

---

## 🔄 Pipeline : le trajet d'une question

```mermaid
sequenceDiagram
    autonumber
    actor U as Utilisateur
    participant G as Garde-fou gr-riskpilot
    participant A as Agent auditpilot-bm
    participant C as Interpréteur de code
    participant R as Recherche de fichiers
    U->>G: « Simule l'audit sans le contrat 1806694 des alevins »
    G->>A: question autorisée
    A->>C: exécute moteur_audit.py sur les contrats et la liste d'exclusion
    C-->>A: tableaux avant · après pays par pays, statuts officiels et simulés
    A->>R: seuils, règles de simulation, suites à donner
    R-->>A: extraits des sections 2, 4, 6 et 7
    A-->>U: simulation présentée comme telle, indicateurs modifiés, interprétation
```

---

## 🧬 Lignage : d'où vient chaque information

```mermaid
flowchart LR
    K[contrats_marches_bm.csv<br/>20 949 contrats réels]
    S[sanctions_bm.csv<br/>1 540 entreprises et personnes exclues]
    P[Programme_Audit_Marches_BM.pdf<br/>8 sections]
    MO{{moteur_audit.py<br/>dans l'interpréteur de code}}
    FS{{Recherche de fichiers<br/>index vs-programme-audit}}
    LLM((gpt-5-mini))
    N[/Rapport au comité d'audit<br/>+ simulations + classeur Excel/]
    E[(Évaluation<br/>12 questions de référence)]
    V[[verifier_audit.py<br/>seconde implémentation]]
    BM[(Banque mondiale<br/>Finances One et liste d'exclusion)]
    BM --> K
    BM --> S
    K --> MO
    S --> MO
    P --> FS
    MO -->|chiffres et statuts| LLM
    FS -->|sections et procédures| LLM
    LLM --> N
    N -.->|comparé à| E
    V -.->|contrôle croisé, 11 indicateurs| MO
```

---

## 🏗️ Architecture

Le schéma d'ensemble figure en tête de page, dans l'Aperçu. Chaque composant porte un nom fixe, repris dans le guide :

| Composant | Nom | Rôle |
|---|---|---|
| Groupe de ressources | `rg-riskpilot` | conteneur Azure, avec un budget d'alerte de 5 € |
| Projet Foundry | `proj-riskpilot` | espace de travail, région Sweden Central, partagé avec les autres agents de la série |
| Modèle | `gpt-5-mini` | déploiement Standard global, facturé uniquement à l'usage |
| Agent | `auditpilot-bm` | instructions d'audit, deux outils, versions successives |
| Moteur d'audit | `moteur_audit.py` | programme d'audit codé une fois pour toutes, exécuté par l'agent |
| Index vectoriel | `vs-programme-audit` | programme d'audit découpé et vectorisé, réservé à cet agent |
| Garde-fou | `gr-riskpilot` | jailbreak et injections indirectes bloqués, contenus nuisibles filtrés |
| Évaluation | `eval-auditpilot` | 12 questions, juge gpt-5-mini, Similarité au seuil de 3 sur 5 |

### Pourquoi un moteur d'audit plutôt que du code improvisé

Un test de Benford ou de fractionnement sur 20 949 lignes doit donner **le même résultat à chaque exécution** : c'est la condition pour qu'un dossier de travail soit revu par un associé ou un régulateur. Laissé libre, un modèle réécrirait les tests à chaque question et finirait par se tromper. Le moteur fige les règles du programme dans un code testé, contrôlé par une seconde implémentation indépendante. Il fait aussi tout le travail déterministe que le modèle pourrait mal recombiner : il affiche pour chaque test les pays en risque avec leur taux, et produit lui-même le tableau avant · après des simulations. L'agent garde le raisonnement, la rédaction et les citations, et chaque chiffre devient **reproductible, rapide et auditable**.

### Les tests d'audit, illustrés avec les données réelles

| Loi de Benford : premier chiffre des 20 928 montants | Écart à Benford par pays |
|:---:|:---:|
| ![Loi de Benford](docs/images/loi_de_benford.svg) | ![Benford par pays](docs/images/benford_par_pays.svg) |

| Test 5 · Part du gré à gré par pays | Test 6 · Poids du premier fournisseur par pays |
|:---:|:---:|
| ![Gré à gré par pays](docs/images/gre_a_gre_par_pays.svg) | ![Concentration par pays](docs/images/concentration_par_pays.svg) |

| Cartographie des risques par pays (section 6) |
|:---:|
| ![Cartographie des risques](docs/images/cartographie_des_risques.png) |

| Simulation : le Burkina Faso sans le contrat 1806694 |
|:---:|
| ![Simulation Burkina Faso](docs/images/simulation_burkina_faso.svg) |

---

## 🛠️ Stack technique

| Domaine | Technologies |
|---|---|
| Plateforme AI | Microsoft Foundry, Foundry Agent Service, nouveau portail Foundry |
| Modèles | gpt-5-mini (agent et juge), text-embedding-3-large (index vectoriel) |
| Outils de l'agent | Interpréteur de code avec moteur d'audit, recherche de fichiers (RAG) |
| Sécurité | Garde-fous Foundry : Prompt Shields, injections indirectes, filtres de contenu |
| Qualité | Évaluations Foundry : Similarité avec des réponses de référence |
| Code | Python, SDK `azure-ai-projects`, `azure-identity`, pandas, openpyxl |
| Audit | ISA 240, 315, 320, 450, 520 et 530 ; loi de Benford et écart absolu moyen de Nigrini ; score robuste ; rapprochement de noms ; sondage par unités monétaires ; Règlement de passation des marchés de la Banque mondiale |
| Données | Banque mondiale, Finances One (jeu DS00005) et liste d'exclusion, licence CC BY 4.0 |
| Gouvernance des coûts | Budget Azure à 5 € avec alertes à 80 % et 100 % |

---

## 📂 Structure du dépôt

```
auditpilot-foundry-agent/
├── agent/
│   ├── instructions_agent.txt          instructions complètes de l'agent
│   ├── moteur_audit.py                 moteur d'audit à joindre à l'interpréteur de code
│   ├── appel_agent.py                  appel de l'agent depuis Python (SDK Foundry)
│   └── requirements.txt
├── donnees/
│   ├── contrats_marches_bm.csv         20 949 contrats réels de la Banque mondiale
│   ├── sanctions_bm.csv                liste d'exclusion de la Banque mondiale
│   └── DICTIONNAIRE.md                 colonnes, sources et licence
├── programme/
│   └── Programme_Audit_Marches_BM.pdf  référentiels, seuils, tests, échantillon, suites, règles
├── evaluation/
│   ├── eval_auditpilot.jsonl           12 questions et réponses de référence
│   ├── synthese_evaluation.csv         indicateurs de l'évaluation
│   ├── resultats_evaluation.csv        note par question
│   └── reponses_agent.csv              réponses de l'agent face aux références
├── outils/
│   ├── verifier_audit.py               seconde implémentation et contrôle croisé du moteur
│   └── requirements.txt
└── docs/
    ├── Guide_Foundry_AuditPilot_Public_5.pdf  guide pas à pas en 10 étapes, avec le cours d'audit
    └── images/
```

---

## 🚀 Reproduire le projet

Le guide complet commence par un cours d'audit en trois pages, illustré avec les vrais résultats, puis détaille chaque clic, chaque valeur à saisir et chaque résultat attendu, jusqu'aux résultats de l'évaluation.

<div align="center">

[![Aperçu du guide AuditPilot : couverture, cours d'audit, cartographie et résultats](docs/images/guide_apercu.png)](https://github.com/abdoulhamiddiallo/auditpilot-foundry-agent/raw/main/docs/Guide_Foundry_AuditPilot_Public_5.pdf)

**[📘 Télécharger le guide en PDF (14 pages)](https://github.com/abdoulhamiddiallo/auditpilot-foundry-agent/raw/main/docs/Guide_Foundry_AuditPilot_Public_5.pdf)**

</div>

En résumé :

| Étape | Où | Ce que vous faites |
|:---:|---|---|
| 1 | `ai.azure.com` | créer le projet `proj-riskpilot`, puis un budget de 5 € |
| 2 | Découvrir › Modèles | déployer `gpt-5-mini` |
| 3 | Build › Agents | créer `auditpilot-bm` et coller [`agent/instructions_agent.txt`](agent/instructions_agent.txt) |
| 4 | Outils › Interpréteur de code | joindre [`agent/moteur_audit.py`](agent/moteur_audit.py) et les deux fichiers de [`donnees/`](donnees) |
| 5 | Outils › Charger des fichiers | indexer le [programme d'audit](https://github.com/abdoulhamiddiallo/auditpilot-foundry-agent/raw/main/programme/Programme_Audit_Marches_BM.pdf) dans `vs-programme-audit` |
| 6 | Garde-fous | créer ou partager `gr-riskpilot` |
| 7 | Playground | poser les questions de test et comparer aux résultats clés |
| 8 | Évaluations | évaluer avec [`evaluation/eval_auditpilot.jsonl`](evaluation/eval_auditpilot.jsonl) |
| 9 | Terminal | appeler l'agent avec [`agent/appel_agent.py`](agent/appel_agent.py) |
| 10 | Portail Azure | tout fermer : rien ne facture à l'arrêt |

> Vous avez déjà construit un agent de la série ? Passez directement à l'étape 3 : même groupe de ressources, même projet, même modèle, même garde-fou.

💶 **Coût :** l'agent ne coûte rien en lui-même. Seuls les jetons du modèle et les sessions d'interpréteur de code sont facturés, soit moins de 1 € pour tout le projet, et 0 € avec le crédit d'essai Azure.

### Appeler l'agent depuis Python

```bash
pip install -r agent/requirements.txt
az login
python agent/appel_agent.py
```

---

## 🔬 Vérifier les chiffres sans AI

Les réponses de référence de l'évaluation ont été calculées hors de l'agent, par une **seconde implémentation** écrite indépendamment du moteur, avec le module `csv` et des boucles explicites plutôt que les regroupements de pandas. Le script recalcule tout à partir des fichiers, puis vérifie que le moteur de l'agent donne exactement les mêmes résultats :

```bash
pip install -r outils/requirements.txt
python outils/verifier_audit.py
```

```
20949 contrats · 9 382 249 401 USD · seuil de signification 46 911 247 USD
Benford : écart absolu moyen 0,0048 sur 20928 montants
Doublons probables : 49 groupes · excédent 22 742 127 USD
Fractionnement : 206 grappes · 31 762 402 USD
Gré à gré : 24,30 % de la valeur
Fournisseurs exclus : 5 contrats · 35 018 950 USD
Échantillon par unités monétaires : intervalle 15 637 082 USD · 600 points de sélection

CONTRÔLE CROISÉ AVEC agent/moteur_audit.py
  ✓ Nombre de contrats                             20 949   écart 0
  ✓ Valeur de la population                 9 382 249 401   écart 0
  ✓ Seuil de signification                     46 911 247   écart 0
  ...
11 indicateurs sur 11 identiques.
```

Les 600 points de sélection tombent sur 467 contrats distincts : un élément clé plus grand que l'intervalle reçoit plusieurs points mais n'est vérifié qu'une fois. Le moteur s'exécute aussi seul et affiche tous les résultats, cartographie et suites à donner comprises : `python agent/moteur_audit.py`.

---

## 📐 Méthodologie

| Étape | Règle appliquée (sections 2 à 5 du programme) |
|---|---|
| Population | tous les contrats des exercices 2020 à 2026, sans exclusion ; les consultants individuels anonymisés par la source restent dans la population mais sont exclus des tests fondés sur le nom |
| Seuils | signification : 0,5 % de la valeur ; remontée : 5 % de la signification ; exposition au-dessus de la signification : ÉLEVÉ, au-dessus de la remontée : MODÉRÉ |
| Loi de Benford | premier chiffre des montants d'au moins 10 USD ; écart absolu moyen de Nigrini ; alerte à 0,012, élevé à 0,015 ; non applicable sous 1 000 montants |
| Valeurs atypiques | score robuste sur le logarithme des montants de chaque catégorie (médiane et écart absolu médian) ; atypique au-delà de 4,5 |
| Doublons probables | même fournisseur, même référence de l'emprunteur, même montant ; excédent = montant × (enregistrements - 1) |
| Fractionnement | contrats de moins de 100 000 USD d'un même fournisseur, projet et catégorie, signés à 30 jours au plus d'écart, dont le total atteint 100 000 USD |
| Gré à gré | part de la valeur attribuée par sélection directe ; modéré à 20 %, élevé à 30 % |
| Concentration | part du premier fournisseur dans la valeur du pays, avec l'indice de Herfindahl ; modéré à 25 %, élevé à 40 % |
| Fournisseurs exclus | noms nettoyés des accents, de la ponctuation et des formes juridiques, similarité d'au moins 95 % ; signature comparée à la période d'exclusion |
| Échantillon | sondage par unités monétaires, confiance de 95 % sans erreur attendue (facteur 3,0) ; intervalle = seuil de signification / 3 ; éléments clés sélectionnés d'office |

> ⚖️ **Règle de présomption.** Un constat analytique signale un risque à examiner : il ne constitue ni une preuve de fraude ni une accusation. Les entreprises citées le sont uniquement à partir de données publiées par la Banque mondiale, et une inscription sur la liste d'exclusion postérieure à la signature d'un contrat ne dit rien de l'exécution de ce contrat.

> 📊 **Données.** Contrats : Banque mondiale, Finances One, jeu DS00005 *Contract Awards in Investment Project Financing*, extraits le 27/10/2026. Exclusions : *World Bank Listing of Ineligible Firms and Individuals*, consultée le 27/10/2026. Licence CC BY 4.0. Détail des colonnes dans [`donnees/DICTIONNAIRE.md`](donnees/DICTIONNAIRE.md).

---

## ✅ Conclusion

AuditPilot montre ce qu'un agent AI doit être pour entrer dans une fonction d'audit : **exact**, parce que chaque chiffre vient d'un moteur validé par une seconde implémentation ; **exhaustif**, parce qu'il teste toute la population avant de tirer un échantillon ; **traçable**, parce que chaque statut cite sa section et chaque suite sa procédure ; **prudent**, parce qu'il constate sans jamais accuser et refuse de toucher à la population ; **mesuré**, parce qu'une évaluation sur des réponses de référence prouve sa qualité avant toute mise en service.

---

## 💡 Mot de la fin

> Un bon auditeur ne cherche pas des coupables : il cherche ce que les chiffres cachent. Un montant géant peut en masquer un autre, et seul un travail exhaustif, chiffré et prudent le révèle.
>
> **Construire pour explorer. Explorer pour comprendre. Et apprendre en chemin.**

---

## 👤 Auteur

**Abdoul Hamid Diallo** · Microsoft Data & AI Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Abdoul_Hamid_Diallo-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/abdoul-hamid-diallo-fabric-data-engineer/)
[![GitHub](https://img.shields.io/badge/GitHub-abdoulhamiddiallo-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/abdoulhamiddiallo)

**Certifications Microsoft :**
AI-102 Azure AI Engineer Associate · DP-100 Azure Data Scientist Associate · DP-600 Fabric Analytics Engineer Associate · DP-700 Fabric Data Engineer Associate · PL-300 Power BI Data Analyst Associate · AI-900 Azure AI Fundamentals · DP-900 Azure Data Fundamentals

**Dans la même série :** [RiskPilot](https://github.com/abdoulhamiddiallo/riskpilot-foundry-agent), le risque de marché d'un fonds de 50 M€ · [ReservePilot](https://github.com/abdoulhamiddiallo/reservepilot-foundry-agent), le provisionnement actuariel et Solvabilité II · [CreditPilot](https://github.com/abdoulhamiddiallo/creditpilot-foundry-agent), le risque de crédit IFRS 9 et Bâle · [ALMPilot](https://github.com/abdoulhamiddiallo/almpilot-foundry-agent), la gestion actif-passif d'une banque.
