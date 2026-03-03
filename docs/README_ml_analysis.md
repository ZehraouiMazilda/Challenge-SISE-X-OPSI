
Colonnes principales :

- Date
- Adresse_IP_Source
- Adresse_IP_Destination
- Protocole
- Port_Destination
- Action (Permit / Deny)
- Identifiant_Regle
- Interface_Entree
- Interface_Sortie

Variables dérivées automatiquement :

- Heure
- Jour_Semaine
- Est_Rejet
- Est_TCP

---

# 🧭 Organisation de l’application

L’application est structurée en 8 onglets, chacun correspondant à une étape analytique précise.

---

## 🔬 1. Descripteurs Comportementaux

### 🎯 Pourquoi ?

Les logs bruts sont difficiles à exploiter directement.  
Chaque adresse IP est donc résumée par un profil comportemental agrégé.

### 📊 Variables construites :

- Nombre_Ports_Distincts
- Nombre_Rejets
- Nombre_Connexions
- Duree_Minutes
- Vitesse_Connexion_Par_Minute
- Ratio_Rejet
- Ratio_TCP
- Port_Max

Ces descripteurs permettent de transformer un flux réseau brut en vecteurs exploitables par les modèles ML.

---

## 🌲 2. Isolation Forest

### 🎯 Objectif

Détection d’anomalies non supervisée.

### ⚙️ Paramètres :

- Contamination (0.01 → 0.20)
- Nombre d’arbres (50 → 500)

### 🧠 Principe

Une anomalie est plus facile à isoler qu’un point normal.  
Plus le score est négatif, plus l’adresse IP est suspecte.

### 📊 Sorties :

- Nombre d’IP suspectes
- Distribution des scores
- Tableau des IP les plus suspectes

---

## 📡 3. Local Outlier Factor (LOF)

### 🎯 Objectif

Détection d’anomalies basée sur la densité locale.

### ⚙️ Paramètres :

- Nombre de voisins (k)
- Taux de contamination

### 🧠 Principe

Compare la densité locale d’une IP à celle de ses voisins.  
Un score élevé signifie un comportement atypique.

### 📈 Sorties :

- Courbe des scores triés
- Nombre d’anomalies détectées
- Statistiques descriptives

---

## 🔭 4. Analyse en Composantes Principales (ACP)

### 🎯 Objectif

Visualiser les données dans un espace réduit pour valider la séparation entre comportements normaux et suspects.

### ⚙️ Méthodologie :

- Standardisation des variables
- PCA jusqu’à 4 composantes

### 📊 Visualisations :

- Plan factoriel (Axes 1 & 2)
- Variance expliquée
- Cercle des corrélations

---

## 🔵 5. K-Means

### 🎯 Objectif

Regrouper automatiquement les adresses IP selon leur comportement.

### ⚙️ Paramètres :

- Nombre maximum de clusters testés (3 → 12)
- Choix final de K basé sur :
  - Méthode du coude (inertie)
  - Score de silhouette

### 📊 Sorties :

- Projection ACP des clusters
- Profil moyen par cluster

---

## 🎯 6. Classification Supervisée

### 🎯 Objectif

Prédire si une connexion sera rejetée ou acceptée.

### 📦 Modèles comparés :

- Régression Logistique (L1 / L2)
- Arbre de Décision CART
- Forêt Aléatoire

### ⚙️ Méthodologie :

- Standardisation des variables
- Validation croisée stratifiée (5 plis)
- Métriques :
  - Accuracy
  - AUC-ROC
  - Écart-type

### 📊 Visualisations :

- Tableau comparatif
- Barplot des performances
- Courbes ROC

---

## 📋 7. Extraction de Règles (Arbre CART)

### 🎯 Objectif

Transformer le modèle en règles lisibles et exploitables.

### ⚙️ Paramètres :

- Profondeur maximale (2 → 6)
- Minimum d’échantillons par feuille

### 📊 Résultats :

- Règles textuelles extraites
- Importance des variables
- Matrice de confusion

---

## 📊 8. Synthèse et Recommandations

### 📈 Analyses finales :

- Évolution temporelle des flux
- Top 10 des ports rejetés
- Distribution horaire du trafic

### ✅ Recommandations proposées :

1. Blocage des IP identifiées comme suspectes.
2. Renforcement des règles sur les ports ciblés.
3. Surveillance accrue aux heures sensibles.
4. Intégration des règles CART dans Iptables.

---

# 🛠 Technologies utilisées

- Streamlit
- Scikit-learn
- Plotly
- Pandas
- NumPy

Modèles utilisés :

- IsolationForest
- LocalOutlierFactor
- KMeans
- LogisticRegression
- DecisionTreeClassifier
- RandomForestClassifier
- PCA

---

# 🚀 Lancement
