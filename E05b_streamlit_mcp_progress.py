import streamlit as st
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

# ==============================================================================
# Demo LLM - Phase E : Étape 5b : Client avec Progress Tracking (UI Temps Réel)
# ==============================================================================
# ASPECT CLÉ : Gérer les appels d'outils asynchrones et afficher les notifications
# de progression au fur et à mesure qu'elles arrivent.
# ==============================================================================

MCP_PROGRESS_URL = "http://127.0.0.1:8003/sse"

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE MCP
# ------------------------------------------------------------------------------

async def mcp_run_combat(hero1, hero2, progress_cb):
    """
    Exécute l'appel à l'outil de combat et redirige les notifications 
    de progrès vers le callback fourni.
    """
    async def wrapped_progress_cb(progress, total, message):
        # Trace dans le terminal pour la démo côté serveur/logique
        print(f"  [MCP CLIENT] Progress: {progress}/{total} - {message}")
        # Appel du callback UI pour l'affichage Streamlit
        await progress_cb(progress, total, message)

    print(f"  [MCP CLIENT] Combat: {hero1} vs {hero2}...")
    async with sse_client(url=MCP_PROGRESS_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Appel à l'outil avec le callback enveloppé
            result = await session.call_tool(
                "simulate_combat", 
                {"hero1": hero1, "hero2": hero2},
                progress_callback=wrapped_progress_cb
            )
            return result.content[0].text if result.content else "Aucun résultat"

# ------------------------------------------------------------------------------
# SECTION 2 : UI STREAMLIT
# ------------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="MCP E05 : Progress", page_icon="⏳", layout="wide")
    st.title("⏳ Phase E : Étape 5 : Suivi de Progression (Progress Tracking)")

    # L'encart didactique a été déplacé dans le Cockpit (Concept).
    st.markdown("---")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("🎮 Lancer le Combat")
        h1 = st.selectbox("Héros 1", ["Iron Man", "Captain America", "Thor", "Hulk", "Black Widow"])
        h2 = st.selectbox("Héros 2", ["Thanos", "Loki", "Ultron", "Hela", "Spider-Man"], index=1)
        
        if st.button("Lancer la simulation", type="primary"):
            st.session_state.start_combat = True
            st.session_state.hero1 = h1
            st.session_state.hero2 = h2

    with col2:
        st.header("📺 Console de Combat")
        if st.session_state.get("start_combat"):
            status_placeholder = st.empty()
            progress_bar = st.progress(0, text="Initialisation...")
            log_placeholder = st.empty()
            logs = []

            # Callback interne à l'UI pour mettre à jour les composants Streamlit
            async def ui_on_progress(progress, total, message):
                percent = int((progress / total) * 100)
                progress_bar.progress(percent, text=f"Progression : {percent}%")
                logs.append(f"⏱️ {message}")
                log_placeholder.code("\n".join(logs))

            # Exécution de la logique MCP
            with status_placeholder.status(f"⚔️ Duel en cours...", expanded=True) as status:
                try:
                    res = asyncio.run(mcp_run_combat(st.session_state.hero1, st.session_state.hero2, ui_on_progress))
                    status.update(label="✅ Terminé", state="complete")
                    st.success(res)
                except Exception as e:
                    status.update(label="❌ Erreur", state="error")
                    st.error(str(e))
            
            st.session_state.start_combat = False
        else:
            st.write("En attente de commande...")

if __name__ == "__main__":
    if "start_combat" not in st.session_state:
        st.session_state.start_combat = False
    main()
