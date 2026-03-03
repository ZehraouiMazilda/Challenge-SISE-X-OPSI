import streamlit as st
from views import home, dashboard, ml_analysis, llm_expert

# Configuration de la page
st.set_page_config(
    page_title="SOC Dashboard | SISE-OPSIE 2026",
    page_icon="🛡️",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.title("🛡️ Sécurité SI")
    st.markdown("---")
    
    selection = st.radio(
        "Navigation",
        ["🏠 Accueil", "📊 Dashboard", "🤖 Machine Learning", "🧠 Expert LLM"],
        index=2
    )
    
    st.markdown("---")
    st.caption("Projet Master SISE 2026")
    st.caption("Fait par...")

# Routage
if selection == "🏠 Accueil":
    home.show()
elif selection == "📊 Dashboard":
    dashboard.show()
elif selection == "🤖 Machine Learning":
    ml_analysis.show()
elif selection == "🧠 Expert LLM":

    llm_expert.show()
