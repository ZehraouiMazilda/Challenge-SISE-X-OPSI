# 🛡️ SENTINEL — Expert RAG en Cybersécurité

## 🎯 Objectif du projet

SENTINEL est un assistant SOC intelligent basé sur une architecture **RAG (Retrieval-Augmented Generation)**.
Il analyse des logs Iptables et répond en langage naturel en s'appuyant uniquement sur les données réelles du CSV.

Ce projet combine :

- Recherche vectorielle locale
- Indexation dynamique des logs
- LLM Llama 3.3 70B via Groq
- Génération de rapports PDF professionnels

---

# 🧠 Architecture RAG

Pipeline complet :

CSV → Chunking → Embedding vectoriel → Indexation → Top-N Retrieval → LLM → Réponse structurée

---

# 🔎 1. Construction des Chunks

Les logs sont transformés en blocs textuels structurés contenant :

- Résumé global (Total, Permit, Deny, pourcentages)
- Top IP sources actives
- Top IP bloquées
- Ports les plus ciblés
- Règles firewall les plus utilisées
- Analyse temporelle
- IP suspectes
- Connexions vers ports sensibles
- Échantillon de logs

Ces chunks constituent la base documentaire du moteur RAG.

---

# 📐 2. Embedding Vectoriel

Un embedding local est généré via une méthode de hashing (512 dimensions).

Principe :
Chaque mot est hashé via MD5 puis projeté dans un vecteur normalisé.

Cela permet :
- Similarité rapide
- Indexation mémoire efficace
- Zéro dépendance à un modèle d'embedding externe

---

# 📊 3. Indexation

Les embeddings sont stockés dans une matrice NumPy.
Un produit scalaire permet de calculer la similarité avec la requête utilisateur.

---

# 🎯 4. Retrieval (Top-N)

Pour chaque question :

1. La requête est vectorisée
2. Similarité calculée avec tous les chunks
3. Sélection des Top-N plus pertinents
4. Injection du contexte dans le prompt système

Le paramètre Top-N est réglable (2 à 8 chunks).

---

# 🤖 5. Modèle LLM

Modèle utilisé :

Llama 3.3 70B Versatile (via Groq API)

Pourquoi ce modèle ?

- Grande capacité analytique
- Excellent raisonnement structuré
- Réponses rapides via Groq (accélération matérielle)
- Très bon équilibre performance / coût

Température : 0.2
Max tokens : 1500

Le prompt impose :

- 200-350 mots
- Sections structurées
- Chiffres précis
- Ton SOC assertif
- Recommandations opérationnelles

---

# 📄 6. Génération de Rapport PDF

Le système peut :

- Lancer plusieurs requêtes RAG ciblées
- Fusionner les chunks pertinents
- Générer un rapport complet structuré
- Exporter en PDF professionnel (FPDF)

Le rapport inclut :

- Résumé exécutif
- Statistiques générales
- Menaces identifiées
- IP suspectes
- Ports ciblés
- Analyse temporelle
- Recommandations prioritaires

---

# 💬 7. Interface Conversationnelle

Fonctionnalités :

- Chat mémoire (historique limité aux 6 derniers échanges)
- Questions suggérées par catégorie
- Affichage optionnel des sources RAG
- Export JSON de la conversation
- Réinitialisation du chat

---

# ⚙️ Paramètres configurables

- Top-N Retrieval
- Affichage des sources
- Génération PDF
- Effacement historique

---

# 🔐 Sécurité

- Réponses basées uniquement sur contexte RAG
- Aucune hallucination autorisée (prompt strict)
- Données locales uniquement
- Clé API sécurisée via .env

---

# 🚀 Lancement

streamlit run llm_expert.py

Assurez-vous que :

- data/data_exm.csv est présent
- GROQ_API_KEY est configurée dans .env

---

# 🏁 Conclusion

SENTINEL illustre une architecture RAG complète :

- Indexation locale optimisée
- Recherche vectorielle efficace
- LLM puissant pour raisonnement SOC
- Génération de rapports automatisée

Ce projet démontre une intégration concrète entre Data Engineering, NLP et Cybersécurité.
