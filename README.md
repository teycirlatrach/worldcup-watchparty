# ⚽ World Cup 2026: Match & Watch-Party Predictor

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Une application web interactive développée avec **Streamlit** pour anticiper les résultats des matchs de la Coupe du Monde 2026 et recommander les meilleures affiches à regarder en direct (*Watch-Parties*) entre amis !

---

## 📌 Description du Projet

L'application **World Cup 2026 Predictor** combine une modélisation statistique du football avec un moteur de recommandation basé sur le spectacle potentiel. 

Elle permet aux utilisateurs :
* De prédire les probabilités de victoire (Domicile / Nul / Extérieur) et le score le plus probable pour n'importe quelle affiche internationale.
* D'obtenir une note d'attractivité **"Watch-Worthiness Score" (sur 10)** afin de savoir si le match vaut la peine d'être regardé en direct ou s'il s'agit d'un risque de purge.

---

## 🧠 Logique Métier & Modèle Algorithmique

### 1. Moteur de Prédiction (Loi de Poisson)
Le modèle de prédiction repose sur la **distribution de Poisson**, largement utilisée dans la modélisation statistique du football :

1. **Calcul des buts attendus ($xG$)** :
   Pour chaque équipe, le nombre de buts attendus est calculé en croisant la moyenne de buts marqués par l'équipe A avec la moyenne de buts encaissés par l'équipe B sur les dernières années :
   $$xG_{\text{Domicile}} = \frac{\text{Buts Marqués}_A + \text{Buts Encaissés}_B}{2}$$
   $$xG_{\text{Extérieur}} = \frac{\text{Buts Marqués}_B + \text{Buts Encaissés}_A}{2}$$

2. **Matrice de probabilités de scores** :
   À partir de ces $xG$, le modèle génère une matrice de probabilités pour chaque score exact (de 0-0 à 5-5) via la formule de Poisson :
   $$P(X = k) = \frac{e^{-\lambda} \cdot \lambda^k}{k!}$$

3. **Probabilités de résultat** :
   En agrégeant la matrice :
   * **Victoire Équipe A** = Somme de la partie inférieure de la matrice.
   * **Match Nul** = Somme de la diagonale.
   * **Victoire Équipe B** = Somme de la partie supérieure de la matrice.

---

### 2. Moteur d'Attractivité (*Watch-Party Excitement Engine*)
L'algorithme de recommandation attribue une note globale de **1.0 à 10.0** basée sur 4 critères clés :

* **Incertitude du résultat (0 à 4.0 points)** : Un match indécis (ex: 35% - 25% - 40%) rapporte le maximum de points, tandis qu'un match déséquilibré est pénalisé.
* **Volume de buts attendus (0 à 3.0 points)** : Le cumuls des $xG$ est pris en compte et plafonné à 4.0 buts pour favoriser le spectacle sans sur-évaluer les défenses passoires.
* **Prestige & Qualité des équipes (Facteur multiplicateur)** : Pour éviter qu'un match entre nations de bas de tableau à forte moyenne de buts encaissés obtienne un 10/10, un bonus de "Choc de Titans" est appliqué uniquement si **les deux nations font partie de l'élite mondiale**.
* **Enjeu de la compétition (+1.0 point)** : Un bonus est appliqué automatiquement pour les matchs à élimination directe (*Knockout*).

---

## 🚀 Fonctionnalités Principales

- 📊 **Prédictions précises** : Probabilités %, $xG$ par équipe et score exact le plus probable.
- 🔥 **Recommandations interactives** : Badges dynamiques (`🔥 MUST WATCH`, `👍 BON MATCH`, `😴 RISQUE DE PURGE`).
- ⚡ **Interface moderne & fluide** : Graphiques interactifs développés avec Plotly et Streamlit.
- 🌍 **Couverture internationale** : Prise en charge des nations qualifiées et potentielles de la Coupe du Monde.

---

## 📁 Structure du Projet

```text  
WorldCup_WatchParty/
│
├── data/
│   ├── results.csv               # Historique des matchs internationaux
│   ├── goalscorers.csv           # Données sur les buteurs
│   └── teams_stats.json          # Statistiques agrégées par équipe (généré)
│
├── app.py                        # Application Streamlit principale
├── excitement_engine.py          # Algorithme du Watch-Score & badges
├── 1_train_match_predictor.py    # Script de traitement des données
├── requirements.txt              # Dépendances Python du projet
└── README.md                     # Documentation
