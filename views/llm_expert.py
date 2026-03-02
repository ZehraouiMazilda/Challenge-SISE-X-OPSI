import streamlit as st
from groq import Groq
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from chromadb.config import Settings
import pandas as pd
import json, os, hashlib, logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from fpdf import FPDF
import unicodedata

logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

GROQ_MODEL      = "llama-3.3-70b-versatile"
EMBED_MODEL     = "paraphrase-multilingual-MiniLM-L12-v2"
CHROMA_PATH     = "./ChromaDB_firewall"
COLLECTION_NAME = "firewall_logs_rag"
TOP_N           = 4

SYSTEM_PROMPT = """Tu es SENTINEL, analyste SOC senior specialise en logs firewall Iptables.
Reponds TOUJOURS en francais. Base tes reponses UNIQUEMENT sur le CONTEXTE RAG fourni.

REGLES DE FORMAT (impression jury) :
- Entre 200 et 350 mots maximum
- Commence DIRECTEMENT par les faits, zero introduction generique
- Utilise des chiffres precis issus des donnees (ex: "720 blocages sur port 22")
- Structure en 2-3 sections courtes avec titres ##
- Maximum 5 bullet points par section, chaque point = 1 fait concret
- Termine par "## Recommandation" avec 2-3 actions precises et actionnables
- Jamais de phrases vagues comme "il est difficile de determiner" ou "en analysant les donnees"
- Si une info n'est pas dans le contexte RAG : une seule phrase courte pour le dire

INDICATEURS DE SEVERITE (1 seul par reponse, a la fin) :
🔴 Critique | 🟠 Eleve | 🟡 Moyen | 🟢 Info

STYLE SOC PROFESSIONNEL :
- Ton assertif et direct, comme un rapport d'incident
- Privilege les verbes d'action : "Bloquer", "Surveiller", "Isoler", "Investiguer"
- Cite les IPs, ports et rule_id exacts quand disponibles dans le contexte"""

REPORT_PROMPT = """Tu es SENTINEL, analyste SOC senior. Genere un rapport de securite complet et professionnel en francais.
Base-toi UNIQUEMENT sur le CONTEXTE RAG fourni.

Le rapport doit suivre cette structure EXACTE :

# RAPPORT D'ANALYSE SÉCURITÉ — SENTINEL SOC
## Résumé Exécutif
(3-4 phrases synthétisant la posture sécurité globale avec chiffres clés)

## 1. Statistiques Générales
(tableau ou liste avec : total logs, permit/deny, protocoles, période couverte)

## 2. Menaces Identifiées
(liste des menaces détectées avec niveau de sévérité et chiffres précis)

## 3. Top IP Suspectes
(top 5-10 IPs avec nombre de blocages et comportement observé)

## 4. Ports les Plus Ciblés
(top 5-8 ports avec service associé et nombre de tentatives)

## 5. Analyse Temporelle
(pics d'activité, heures sensibles, tendances)

## 6. Règles Firewall
(règles les plus sollicitées, règles potentiellement inutilisées)

## 7. Recommandations Prioritaires
(5-8 actions concrètes classées par priorité 🔴🟠🟡)

## Conclusion
(2-3 phrases de synthèse)

---
Rapport généré par SENTINEL · Projet SISE-OPSIE 2026
Sois précis, professionnel, cite des chiffres réels issus du contexte."""

SUGGESTED_QUESTIONS = {
    "🔍 Détection": [
        "Quelles IP montrent des patterns de scan de ports ?",
        "Y a-t-il des signes d'attaque brute force sur FTP ou SSH ?",
        "Identifie les comportements anormaux dans les logs",
        "Quels flux correspondent a un potentiel DDoS ?",
    ],
    "📊 Statistiques": [
        "Quels sont les ports les plus cibles par les Deny ?",
        "Donne-moi le top 5 des IP sources les plus actives",
        "Repartition TCP/UDP sur les connexions rejetees ?",
        "Analyse les pics d'activite par plage horaire",
    ],
    "🛡️ Sécurité": [
        "Quelles regles firewall semblent inutilisees ?",
        "IP hors plan d'adressage 159.84.x.x ?",
        "Recommandations pour durcir les regles Iptables",
        "Connexions suspectes vers ports sensibles (22, 21, 3306) ?",
    ],
    "🧠 Analytique": [
        "Compare le trafic TCP vs UDP en termes de risque",
        "Quels rule_id concentrent le plus de blocages ?",
        "Patterns temporels dans les attaques ?",
        "Synthese globale de la posture securite du SI",
    ],
}

CSS = """<style>
.rag-hero{background:linear-gradient(135deg,#080c14 0%,#0d1528 60%,#160a28 100%);
  border:1px solid rgba(0,212,255,0.12);border-radius:16px;padding:2rem 2.5rem;margin-bottom:1.5rem;}
.rag-hero h2{color:#00d4ff !important;font-size:1.5rem;margin:0 0 0.4rem 0;}
.rag-hero p{color:#6b7a99;font-size:0.88rem;margin:0;}
.sbar{display:flex;gap:1.5rem;align-items:center;flex-wrap:wrap;background:#0e1420;
  border:1px solid rgba(0,212,255,0.12);border-radius:10px;padding:0.7rem 1.2rem;margin-bottom:0.8rem;}
.sdot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:5px;}
.sg{background:#10b981;box-shadow:0 0 5px #10b981;}
.sb{background:#00d4ff;box-shadow:0 0 5px #00d4ff;}
.sr{background:#ff4d6d;box-shadow:0 0 5px #ff4d6d;}
.si{font-size:0.75rem;color:#6b7a99;display:flex;align-items:center;}
.sv{color:#e2e8f0;font-weight:600;margin-left:4px;font-size:0.72rem;}
.pip{display:flex;align-items:center;gap:0.4rem;flex-wrap:wrap;font-size:0.68rem;color:#6b7a99;margin-bottom:1rem;}
.ps{background:#141c2e;border:1px solid rgba(0,212,255,0.12);border-radius:5px;padding:0.18rem 0.5rem;color:#7b61ff;}
.src-chunk{background:rgba(123,97,255,0.05);border-left:3px solid #7b61ff;
  border-radius:0 8px 8px 0;padding:0.6rem 0.9rem;font-size:0.72rem;color:#6b7a99;
  margin-top:0.4rem;font-family:monospace;line-height:1.6;}
</style>"""


# ── ChromaDB ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def init_chroma():
    ef     = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    client = chromadb.PersistentClient(
        path=CHROMA_PATH, settings=Settings(anonymized_telemetry=False)
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )


# ── Build chunks ──────────────────────────────────────────────────────────
def build_chunks(df: pd.DataFrame) -> list:
    chunks  = []
    total   = len(df)
    permits = int((df["action"] == "Permit").sum()) if "action" in df.columns else 0
    denies  = int((df["action"] == "Deny").sum())   if "action" in df.columns else 0
    proto   = df["protocol"].value_counts().to_dict() if "protocol" in df.columns else {}

    chunks.append(
        f"RESUME GLOBAL LOGS FIREWALL\n"
        f"Total: {total:,} | Permit: {permits:,} ({permits/total*100:.1f}%) | "
        f"Deny: {denies:,} ({denies/total*100:.1f}%)\nProtocoles: {proto}"
    )
    if "ip_source" in df.columns:
        ti  = df["ip_source"].value_counts().head(20).to_dict()
        tid = df[df["action"]=="Deny"]["ip_source"].value_counts().head(20).to_dict() if "action" in df.columns else {}
        chunks.append(f"TOP IP SOURCES ACTIVES\n{ti}\n\nTOP IP SOURCES BLOQUEES\n{tid}")

    if "dest_port" in df.columns:
        pn  = {21:"FTP",22:"SSH",23:"Telnet",53:"DNS",80:"HTTP",443:"HTTPS",
               3306:"MySQL",8080:"HTTP-Alt",3389:"RDP",445:"SMB",137:"NetBIOS"}
        tp  = df["dest_port"].value_counts().head(20)
        tpd = df[df["action"]=="Deny"]["dest_port"].value_counts().head(20) if "action" in df.columns else pd.Series()
        chunks.append(
            "PORTS CIBLES\n" +
            "\n".join([f"Port {p}({pn.get(p,'?')}): {c}" for p,c in tp.items()]) +
            "\nPORTS BLOQUES\n" +
            "\n".join([f"Port {p}({pn.get(p,'?')}): {c}" for p,c in tpd.items()])
        )

    if "rule_id" in df.columns:
        r  = df["rule_id"].value_counts().head(15).to_dict()
        rd = df[df["action"]=="Deny"]["rule_id"].value_counts().head(10).to_dict() if "action" in df.columns else {}
        chunks.append(f"REGLES FIREWALL\n{r}\n\nREGLES AVEC DENY\n{rd}")

    if "date" in df.columns:
        try:
            dft       = df.copy()
            dft["date"] = pd.to_datetime(dft["date"])
            dft["h"]  = dft["date"].dt.hour
            bh        = dft.groupby("h").size()
            dh        = dft[dft["action"]=="Deny"].groupby("h").size() if "action" in dft.columns else pd.Series()
            chunks.append(
                f"ANALYSE TEMPORELLE\nPeriode: {dft['date'].min()} -> {dft['date'].max()}\n"
                f"Heure pic total: {int(bh.idxmax())}h | Heure pic deny: {int(dh.idxmax()) if not dh.empty else 'N/A'}h\n"
                "Distribution horaire:\n" + "\n".join([f"  {h}h: {c}" for h,c in bh.items()])
            )
        except Exception:
            pass

    if "ip_source" in df.columns and "action" in df.columns:
        hi  = df[df["action"]=="Deny"]["ip_source"].value_counts()
        hi  = hi[hi > hi.quantile(0.95)].head(20)
        ext = [ip for ip in df["ip_source"].unique() if not str(ip).startswith("159.84")][:30]
        chunks.append(
            "IP SUSPECTES (deny eleve top 5%)\n" +
            "\n".join([f"{ip}: {c} blocages" for ip,c in hi.items()]) +
            "\nIP HORS PLAN ADRESSAGE (pas 159.84.x.x)\n" + "\n".join(ext[:20])
        )

    if all(c in df.columns for c in ["action","dest_port"]):
        s = df[(df["action"]=="Deny") & (df["dest_port"].isin([21,22,23,3306,3389,445,137]))].head(50)
        if not s.empty:
            chunks.append("CONNEXIONS SUSPECTES PORTS SENSIBLES\n" + s.to_string(index=False))

    sample = df.sample(min(500, len(df)), random_state=42)
    for i in range(0, len(sample), 500):
        chunks.append(f"ECHANTILLON LOGS {i}-{i+400}:\n" + sample.iloc[i:i+400].to_string(index=False))

    return chunks


def ingest(df: pd.DataFrame, collection) -> int:
    h = hashlib.md5(pd.util.hash_pandas_object(df.head(500)).values).hexdigest()
    if st.session_state.get("rag_hash") == h:
        return st.session_state.get("rag_n", 0)
    try:
        ids = collection.get()["ids"]
        if ids:
            collection.delete(ids=ids)
    except Exception:
        pass
    chunks = build_chunks(df)
    for i in range(0, len(chunks), 50):
        b = chunks[i:i+50]
        collection.add(documents=b, ids=[f"c{i+j}" for j in range(len(b))])
    st.session_state["rag_hash"] = h
    st.session_state["rag_n"]    = len(chunks)
    return len(chunks)


def retrieve(query: str, collection, top_n: int) -> list:
    r = collection.query(query_texts=[query], n_results=top_n)
    return r["documents"][0] if r["documents"] else []


def call_groq(question: str, ctx_chunks: list, history: list) -> str:
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        return "Cle GROQ_API_KEY manquante dans .env"
    ctx  = "\n\n---\n\n".join([c[:800] for c in ctx_chunks])
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"CONTEXTE RAG (donnees reelles):\n\n{ctx}"},
    ]
    for m in history[-6:]:
        msgs.append({"role": m["role"], "content": m["content"]})
    msgs.append({"role": "user", "content": question})
    try:
        r = Groq(api_key=key).chat.completions.create(
            model=GROQ_MODEL, messages=msgs, max_tokens=1500, temperature=0.2
        )
        return r.choices[0].message.content
    except Exception as e:
        err = str(e)
        if "401" in err: return "Cle API invalide. Verifiez GROQ_API_KEY."
        if "429" in err: return "Limite de requetes atteinte. Attendez quelques secondes."
        return f"Erreur Groq: {err}"


# ── Génération rapport PDF ────────────────────────────────────────────────
def generate_report_text(collection, df) -> str:
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        return "Cle GROQ_API_KEY manquante."

    queries = [
        "resume global statistiques logs firewall",
        "IP suspectes attaques detectees",
        "ports cibles blocages deny",
        "regles firewall utilisation",
        "analyse temporelle pics activite",
    ]
    all_chunks = []
    for q in queries:
        for c in retrieve(q, collection, top_n=3):
            if c not in all_chunks:
                all_chunks.append(c)

    ctx  = "\n\n---\n\n".join([c[:600] for c in all_chunks[:12]])
    msgs = [
        {"role": "system", "content": REPORT_PROMPT},
        {"role": "system", "content": f"CONTEXTE RAG COMPLET:\n\n{ctx}"},
        {"role": "user",   "content": "Génère le rapport de sécurité complet basé sur ces données."}
    ]
    try:
        r = Groq(api_key=key).chat.completions.create(
            model=GROQ_MODEL, messages=msgs, max_tokens=3000, temperature=0.1
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Erreur generation rapport: {e}"


def build_pdf(report_text: str, df) -> bytes:
    import unicodedata

    def clean_text(text: str) -> str:
        replacements = {
            "🔴":"[CRITIQUE]","🟠":"[ELEVE]","🟡":"[MOYEN]","🟢":"[INFO]",
            "✅":"[OK]","⚠️":"[!]","🛡️":"[SEC]","📊":"[STAT]",
            "🔍":"[DETECT]","🧠":"[ANALYSE]","💡":"[INFO]","•":"-","→":"->",
            "—":"-","–":"-","'":"'","'":"'",""":'"',""":'"',"«":'"',"»":'"',
        }
        for char, rep in replacements.items():
            text = text.replace(char, rep)
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", errors="ignore").decode("ascii")
        return text

    clean = clean_text(report_text)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ── En-tête ──
    pdf.set_fill_color(8, 12, 20)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(0, 212, 255)
    pdf.set_xy(15, 10)
    pdf.cell(0, 10, "SENTINEL - Rapport d'Analyse Securite", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(107, 122, 153)
    pdf.set_xy(15, 22)
    pdf.cell(0, 6, f"Projet SISE-OPSIE 2026  -  Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}  -  Powered by SENTINEL RAG", ln=True)
    pdf.set_xy(15, 30)

    total  = len(df) if df is not None else 0
    denies = int((df["action"]=="Deny").sum()) if df is not None and "action" in df.columns else 0
    pdf.cell(0, 6, f"Logs analyses : {total:,}  -  Deny : {denies:,} ({denies/total*100:.1f}%)  -  Modele : Llama 3.3 70B via Groq", ln=True)

    pdf.ln(18)
    pdf.set_text_color(30, 30, 30)

    # Largeur utile : 210 - 15 (gauche) - 15 (droite) = 180
    W = 180

    for line in clean.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 15)
            pdf.set_text_color(0, 100, 180)
            pdf.set_fill_color(230, 240, 255)
            pdf.set_x(15)
            pdf.multi_cell(W, 9, line[2:], fill=True)
            pdf.ln(2)
        elif line.startswith("## "):
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(0, 80, 150)
            pdf.ln(3)
            pdf.set_x(15)
            pdf.multi_cell(W, 8, line[3:])
            pdf.set_draw_color(0, 150, 200)
            pdf.set_line_width(0.4)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(2)
        elif line.startswith("- ") or line.startswith("* "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.set_x(18)
            pdf.multi_cell(W - 3, 6, "- " + line[2:])
        elif line.startswith("---"):
            pdf.set_draw_color(200, 200, 200)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(3)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.set_x(15)
            pdf.multi_cell(W, 6, line)

    # ── Pied de page ──
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, f"SENTINEL SOC - SISE-OPSIE 2026 - Page {pdf.page_no()}", align="C")

    return bytes(pdf.output())


# ── Main view ─────────────────────────────────────────────────────────────
def show():
    st.markdown(CSS, unsafe_allow_html=True)

    st.markdown("""
    <div class="rag-hero">
        <h2>🛡️ SENTINEL — Expert RAG Cybersécurité</h2>
        <p>Analyse de vos logs firewall Iptables par RAG · ChromaDB + Embeddings MiniLM-L12 + Llama 3.3 70B via Groq<br>
        Les réponses sont ancrées dans vos données réelles grâce à la recherche vectorielle sémantique.</p>
    </div>
    """, unsafe_allow_html=True)

    for k, v in [("llm_history",[]),("rag_hash",None),("rag_n",0),("show_src",False),("report_bytes",None)]:
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Chargement CSV si pas encore dans session_state ──────────────
    if "df" not in st.session_state or st.session_state["df"] is None:
        try:
            st.session_state["df"] = pd.read_csv(
                Path(__file__).resolve().parent.parent / "data" / "data_exm.csv"
            )
        except FileNotFoundError:
            st.error("⚠️ Fichier introuvable : data/data_exm.csv")
            return

    df         = st.session_state.get("df", None)
    rag_ready  = False
    collection = None

    if df is not None and not df.empty:
        try:
            collection    = init_chroma()
            ingest_needed = st.session_state.get("rag_hash") is None
            if ingest_needed:
                with st.spinner("⚙️ Initialisation RAG — première fois uniquement…"):
                    ingest(df, collection)
            else:
                try:
                    if collection.count() == 0:
                        ingest(df, collection)
                except Exception:
                    ingest(df, collection)
            rag_ready     = True
        except Exception as e:
            st.error(f"Erreur RAG : {e}")

    n_chunks = st.session_state.get("rag_n", 0)
    total    = len(df) if df is not None else 0
    denies   = int((df["action"]=="Deny").sum())   if df is not None and "action" in df.columns else 0
    permits  = total - denies
    dot      = "sg" if rag_ready else "sr"

    st.markdown(f"""
    <div class="sbar">
        <div class="si"><span class="sdot {dot}"></span>RAG <span class="sv">{'Actif' if rag_ready else 'Inactif'}</span></div>
        <div class="si"><span class="sdot sb"></span>Chunks <span class="sv">{n_chunks}</span></div>
        <div class="si"><span class="sdot sb"></span>Logs <span class="sv">{total:,}</span></div>
        <div class="si"><span class="sdot sg"></span>Permit <span class="sv">{permits:,}</span></div>
        <div class="si"><span class="sdot sr"></span>Deny <span class="sv">{denies:,}</span></div>
        <div class="si">Modèle <span class="sv">Llama 3.3 70B · Groq</span></div>
    </div>
    <div class="pip">
        <span class="ps">📄 CSV</span><span>→</span>
        <span class="ps">✂️ Chunking</span><span>→</span>
        <span class="ps">🧬 MiniLM Embeddings</span><span>→</span>
        <span class="ps">🗄️ ChromaDB</span><span>→</span>
        <span class="ps">🔍 Top-N Retrieval</span><span>→</span>
        <span class="ps">🤖 Llama 3.3 70B</span><span>→</span>
        <span class="ps">💬 Réponse</span>
    </div>
    """, unsafe_allow_html=True)

    col_chat, col_side = st.columns([3, 1], gap="medium")

    # ── Panneau droit ─────────────────────────────────────────────────
    with col_side:
        st.markdown("#### 💡 Questions suggérées")
        for cat, qs in SUGGESTED_QUESTIONS.items():
            with st.expander(cat, expanded=(cat == "🔍 Détection")):
                for q in qs:
                    if st.button(q, key=f"s_{abs(hash(q))}", use_container_width=True):
                        st.session_state["llm_pending"] = q

        st.markdown("#### ⚙️ Paramètres RAG")
        top_n = st.slider("Chunks Top-N", 2, 8, TOP_N,
                          help="Nombre de chunks envoyés au LLM comme contexte")
        st.session_state.show_src = st.toggle("Afficher sources RAG", False)

        st.markdown("---")

        # ── Rapport PDF ────────────────────────────────────────────
        st.markdown("#### 📄 Rapport PDF")
        if rag_ready:
            if st.button("⚡ Générer le rapport", use_container_width=True, type="primary"):
                with st.spinner("Génération du rapport en cours…"):
                    report_text                    = generate_report_text(collection, df)
                    pdf_bytes                      = build_pdf(report_text, df)
                    st.session_state["report_bytes"] = pdf_bytes
                st.success("Rapport généré !")

            if st.session_state.get("report_bytes"):
                st.download_button(
                    label="📥 Télécharger le rapport PDF",
                    data=st.session_state["report_bytes"],
                    file_name=f"SENTINEL_rapport_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

        st.markdown("---")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Effacer la conversation", use_container_width=True):
            st.session_state.llm_history = []
            st.rerun()
        if st.session_state.llm_history:
            st.download_button(
                "📥 Exporter chat (JSON)",
                data=json.dumps(st.session_state.llm_history, ensure_ascii=False, indent=2),
                file_name=f"sentinel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

    # ── Zone de chat ──────────────────────────────────────────────────
    with col_chat:
        if not rag_ready:
            st.warning("⚠️ Aucune donnée chargée. Vérifiez que `df` est dans `st.session_state`.")
            return

        if not st.session_state.llm_history:
            with st.chat_message("assistant"):
                st.markdown(
                    f"👋 Bonjour ! Je suis **SENTINEL**, votre analyste SOC IA.\n\n"
                    f"✅ **{n_chunks} chunks** indexés dans ChromaDB depuis vos logs firewall.\n\n"
                    f"🔍 Mes réponses s'appuient sur vos **données réelles** "
                    f"via recherche vectorielle sémantique (Top-{top_n} chunks).\n\n"
                    "Posez une question ou choisissez une suggestion →"
                )
        else:
            for i, msg in enumerate(st.session_state.llm_history):
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg["role"] == "assistant" and st.session_state.show_src:
                        src = st.session_state.get(f"src_{i}", [])
                        if src:
                            with st.expander(f"🔍 {len(src)} sources RAG", expanded=False):
                                for j, c in enumerate(src):
                                    st.markdown(
                                        f'<div class="src-chunk"><b>📄 Chunk {j+1}/{len(src)}</b><br>'
                                        f'{c[:350]}{"..." if len(c)>350 else ""}</div>',
                                        unsafe_allow_html=True
                                    )

        pending    = st.session_state.pop("llm_pending", None)
        user_input = st.chat_input("Interrogez SENTINEL sur vos logs firewall…")
        question   = pending or user_input

        if question:
            with st.chat_message("user"):
                st.markdown(question)

            with st.spinner("🔍 Recherche vectorielle dans ChromaDB…"):
                ctx = retrieve(question, collection, top_n)

            ans_idx     = len(st.session_state.llm_history) + 1
            st.session_state[f"src_{ans_idx}"] = ctx
            hist_before = st.session_state.llm_history.copy()
            st.session_state.llm_history.append({"role": "user", "content": question})

            with st.chat_message("assistant"):
                with st.spinner("🤖 SENTINEL génère la réponse…"):
                    answer = call_groq(question, ctx, hist_before)
                st.markdown(answer)
                if st.session_state.show_src and ctx:
                    with st.expander(f"🔍 {len(ctx)} sources utilisées", expanded=False):
                        for j, c in enumerate(ctx):
                            st.markdown(
                                f'<div class="src-chunk"><b>📄 Chunk {j+1}/{len(ctx)}</b><br>'
                                f'{c[:350]}{"..." if len(c)>350 else ""}</div>',
                                unsafe_allow_html=True
                            )

            st.session_state.llm_history.append({"role": "assistant", "content": answer})
            st.rerun()