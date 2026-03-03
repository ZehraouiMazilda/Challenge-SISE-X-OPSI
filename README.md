# 🛡️ Challenge SISE x OPSIE — Plateforme Complète d’Analyse Cyber

## 🎯 Présentation du Projet

Ce projet regroupe **trois modules complémentaires** pour l’analyse avancée de logs Iptables :

1. 📊 Dashboard descriptif interactif  
2. 🤖 Module Machine Learning (détection & classification)  
3. 🧠 Module RAG + LLM (SENTINEL SOC Assistant)

L'objectif est de proposer une **chaîne complète d’analyse sécurité** allant de la visualisation simple jusqu’à l’assistance SOC augmentée par LLM.

---

# 🏗️ Architecture Globale

Logs CSV → Dashboard / ML / RAG → Llama 3.3 70B (Groq) → Analyse & Rapport PDF

---

# 📦 Installation via Git

## 1️⃣ Cloner le dépôt

```bash
git clone https://github.com/VOTRE-REPO/Challenge-SISExOPSIE.git
cd Challenge-SISExOPSIE
```

---

# 🐳 Lancement avec Docker

## 2️⃣ Construire l’image Docker

Depuis la racine du projet :

```bash
docker build -t sentinel-soc .
```

## 3️⃣ Créer le fichier .env

Créer un fichier `.env` à la racine du projet :

```env
GROQ_API_KEY=VOTRE_CLE_GROQ_ICI
```

⚠️ Ne jamais commit ce fichier.

## 4️⃣ Lancer le conteneur

```bash
docker run -p 8501:8501 --env-file .env sentinel-soc
```

Puis ouvrir dans le navigateur :

http://localhost:8501

---

# 💻 Lancement Local (sans Docker)

Créer un environnement virtuel :

```bash
python -m venv venv
```

Activation :

Windows :
```bash
venv\Scripts\activate
```

Mac/Linux :
```bash
source venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Lancer l'application :

```bash
streamlit run app.py
```

---

# 🔑 Configuration du LLM (Groq)

1️⃣ Aller sur https://console.groq.com/  
2️⃣ Créer un compte  
3️⃣ Générer une clé API  
4️⃣ La placer dans `.env` :

```env
GROQ_API_KEY=VOTRE_CLE_ICI
```

Modèle utilisé :
```
llama-3.3-70b-versatile
```

---

# 📄 Modules Inclus

## 📊 Dashboard

- Vue globale Permit / Deny  
- Filtres RFC 6056  
- Analyse TCP vs UDP  
- Top IP  
- Export CSV  

## 🤖 Machine Learning

- Isolation Forest  
- LOF  
- K-Means  
- Régression Logistique  
- Arbre CART  
- Random Forest  
- ACP  

## 🧠 RAG + LLM

- Chunking des logs  
- Embedding vectoriel local  
- Indexation NumPy  
- Top-N Retrieval  
- Génération structurée via Llama 3.3 70B  
- Export PDF  

---

# 🔐 Sécurité

- Clé API protégée via `.env`  
- RAG strictement basé sur données locales  
- Prompt contraint pour éviter hallucinations  

---

# 👨‍🎓 Contexte Académique

Projet réalisé dans le cadre du challenge **SISE x OPSIE 2026**.

### Auteurs

- Maissa Lajimi  
- Aya Mecheri  
- Mazilda Zehraoui  

---

# 🚀 Conclusion

Une plateforme SOC moderne combinant :

Dashboard + Machine Learning + RAG + LLM + Génération PDF

Intégration complète Data Engineering, IA et Cybersécurité.

