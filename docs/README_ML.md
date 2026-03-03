# ⚙️ Analyse par Apprentissage Automatique des Logs Iptables

## 🎯 Objectif du projet

Cette application Streamlit permet d'analyser des logs réseau issus d'un
pare-feu Iptables afin de :

-   Détecter automatiquement des comportements suspects
-   Comparer plusieurs modèles d'apprentissage automatique
-   Extraire des règles de sécurité interprétables
-   Produire des recommandations opérationnelles

Le projet combine des approches non supervisées, supervisées et des
outils de visualisation avancée.

------------------------------------------------------------------------

# 🗂 Données utilisées

Fichier attendu :

data/data_exm.csv

Colonnes principales :

-   Date
-   Adresse_IP_Source
-   Adresse_IP_Destination
-   Protocole
-   Port_Destination
-   Action (Permit / Deny)
-   Identifiant_Regle
-   Interface_Entree
-   Interface_Sortie

Variables dérivées automatiquement :

-   Heure
-   Jour_Semaine
-   Est_Rejet
-   Est_TCP

------------------------------------------------------------------------

# 🧭 Organisation de l'application

L'application est structurée en 8 onglets, chacun correspondant à une
étape analytique précise.

------------------------------------------------------------------------

## 🔬 1. Descripteurs Comportementaux

Les logs bruts sont transformés en profils comportementaux par adresse
IP.

Variables construites :

-   Nombre_Ports_Distincts
-   Nombre_Rejets
-   Nombre_Connexions
-   Duree_Minutes
-   Vitesse_Connexion_Par_Minute
-   Ratio_Rejet
-   Ratio_TCP
-   Port_Max

------------------------------------------------------------------------

## 🌲 2. Isolation Forest

Détection d'anomalies non supervisée.

Paramètres : - Contamination (0.01 → 0.20) - Nombre d'arbres (50 → 500)

------------------------------------------------------------------------

## 📡 3. Local Outlier Factor (LOF)

Détection basée sur la densité locale.

Paramètres : - Nombre de voisins (k) - Taux de contamination

------------------------------------------------------------------------

## 🔭 4. Analyse en Composantes Principales (ACP)

Visualisation factorielle des comportements.

-   Standardisation
-   Projection sur axes principaux
-   Variance expliquée
-   Cercle des corrélations

------------------------------------------------------------------------

## 🔵 5. K-Means

Clustering non supervisé des comportements.

-   Méthode du coude
-   Score de silhouette
-   Projection ACP des clusters

------------------------------------------------------------------------

## 🎯 6. Classification Supervisée

Modèles comparés :

-   Régression Logistique (L1 / L2)
-   Arbre CART
-   Forêt Aléatoire

Validation croisée stratifiée (5 plis) avec métriques Accuracy et
AUC-ROC.

------------------------------------------------------------------------

## 📋 7. Extraction de Règles (CART)

Transformation de l'arbre en règles exploitables pour le pare-feu.

------------------------------------------------------------------------

## 📊 8. Synthèse

Analyses finales :

-   Évolution temporelle des flux
-   Top ports rejetés
-   Distribution horaire

Recommandations opérationnelles fournies.

------------------------------------------------------------------------

# 🛠 Technologies utilisées

-   Streamlit
-   Scikit-learn
-   Plotly
-   Pandas
-   NumPy

------------------------------------------------------------------------

# 🚀 Lancement

streamlit run ml_analysis.py

Vérifier la présence du fichier : data/data_exm.csv
