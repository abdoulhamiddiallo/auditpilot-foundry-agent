# 📖 Dictionnaire des données

Les deux fichiers de ce dossier sont des **données réelles publiées par la Banque mondiale**, sous licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.fr). Seuls les noms de colonnes ont été traduits en français : les valeurs (catégories, méthodes de passation, motifs d'exclusion) sont conservées telles que publiées, en anglais, et le moteur d'audit les traduit à l'affichage.

---

## `contrats_marches_bm.csv` · 20 949 contrats

**Source :** Banque mondiale, Finances One, jeu de données DS00005 *Contract Awards in Investment Project Financing*, issu du système de suivi des marchés STEP.
**Périmètre :** contrats attribués sur financement de projets d'investissement de la Banque mondiale dans les huit pays de l'UEMOA (Bénin, Burkina Faso, Côte d'Ivoire, Guinée-Bissau, Mali, Niger, Sénégal, Togo) et en Guinée, exercices 2020 à 2026 de la Banque (signatures du 1er juillet 2019 au 30 juin 2026).
**Extraction :** 27/10/2026.

| Colonne | Contenu | Exemple |
|---|---|---|
| `numero_contrat_bm` | identifiant du contrat attribué par la Banque mondiale | `1806694` |
| `reference_emprunteur` | référence du marché chez l'emprunteur | `CI-PDC2V-408956-CS-CDS` |
| `pays_emprunteur` | pays qui emprunte et passe le marché | `Burkina Faso` |
| `exercice_bm` | exercice de la Banque mondiale (juillet à juin) | `2025` |
| `date_signature` | date de signature du contrat, AAAA-MM-JJ | `2024-08-23` |
| `id_projet` · `nom_projet` | projet financé | `P178598` |
| `pratique_mondiale` | domaine du projet | `Agriculture;Industry & Trade/Ser` |
| `categorie` | Goods, Works, Consultant Services, Non-consulting Services | `Goods` |
| `methode_passation` | méthode de sélection du fournisseur | `Direct Selection` (gré à gré) |
| `type_revue` | revue de la Banque avant (Prior) ou après (Post) attribution | `Post` |
| `fournisseur` · `id_fournisseur` · `pays_fournisseur` | titulaire du contrat | `MOBISOFT` |
| `montant_usd` | montant du contrat en dollars américains | `474643917.0` |
| `objet_du_contrat` | description publiée du marché | `Acquisition de 2 000 000 de souches…` |

| Répartition | Valeurs |
|---|---|
| Pays | Côte d'Ivoire 4 914 · Burkina Faso 4 393 · Niger 3 315 · Sénégal 2 614 · Mali 1 981 · Bénin 1 670 · Guinée 975 · Togo 757 · Guinée-Bissau 330 |
| Catégories | services de consultants 9 211 · fournitures 6 405 · travaux 3 658 · services autres que de consultants 1 675 |
| Méthodes principales | demande de cotations 7 070 · consultant individuel 3 483 · appel d'offres 3 302 · gré à gré 3 120 · qualification des consultants 2 598 |

> Les 3 483 consultants individuels sont anonymisés par la source sous le nom `INDIVIDUAL CONSULTANT` : ils restent dans la population, mais sont exclus des tests fondés sur le nom du fournisseur (doublons, concentration, exclusions).

---

## `sanctions_bm.csv` · 1 540 entreprises et personnes

**Source :** Banque mondiale, *World Bank Listing of Ineligible Firms and Individuals*, page publique consultée le 27/10/2026.

| Colonne | Contenu |
|---|---|
| `nom` | entreprise ou personne exclue |
| `immatriculation` | numéro d'immatriculation publié, quand il existe |
| `adresse` · `pays` | adresse et pays publiés |
| `debut_exclusion` · `fin_exclusion` | période d'inéligibilité ; `en cours` ou `permanente` quand aucune date de fin n'est publiée |
| `motif` | motif publié par la Banque mondiale, par exemple `Fraudulent Practice` |

> Une inscription sur cette liste est un fait publié par la Banque mondiale. Le croisement avec les contrats signale un risque à examiner : ce n'est ni une preuve ni une accusation (section 8 du programme d'audit).

---

## Retrouver les données à la source

| Données | Où |
|---|---|
| Contrats | [financesone.worldbank.org, jeu DS00005](https://financesone.worldbank.org/contract-awards-in-investment-project-financing-since-fy-2020/DS00005), avec son [explorateur d'API](https://financesone.worldbank.org/api-explorer?id=DS00005) : filtre sur `borrower_country` et `fiscal_year` |
| Exclusions | [worldbank.org, liste des entreprises et personnes exclues](https://www.worldbank.org/en/projects-operations/procurement/debarred-firms) |

Les données de la Banque mondiale évoluent chaque jour : une nouvelle extraction peut donner des chiffres légèrement différents de ceux de ce dépôt, qui sont figés au 27/10/2026 pour que chaque résultat reste vérifiable.
