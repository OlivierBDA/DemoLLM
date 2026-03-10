import streamlit as st
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

# ==============================================================================
# Demo LLM - Phase E : Étape 4b : Explorateur avec Templates (Version RÉSEAU)
# ==============================================================================
# ASPECT CLÉ : Le client peut appeler des ressources "paramétrées".
# Idéal pour accéder à des bases de connaissances massives (Doc on-demand).
# ==============================================================================

MCP_TEMPLATES_URL = "http://127.0.0.1:8002/sse"

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE MCP
# ------------------------------------------------------------------------------

async def mcp_discover_all():
    """Découvre à la fois les ressources statiques et les modèles."""
    print("  [MCP CLIENT] Discovery: Interrogation globale du serveur 8002...")
    async with sse_client(url=MCP_TEMPLATES_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            resources = await session.list_resources()
            templates = await session.list_resource_templates()
            return resources.resources, templates.resourceTemplates

async def mcp_read(uri):
    """Lit une ressource (qu'elle soit issue d'un template ou statique)."""
    print(f"  [MCP CLIENT] Reading: Appel de l'URI : {uri}")
    async with sse_client(url=MCP_TEMPLATES_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.read_resource(uri)
            return result.contents[0].text if result.contents else "Vide"

# ------------------------------------------------------------------------------
# SECTION 2 : UI STREAMLIT
# ------------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="MCP E04 : Templates", page_icon="🧩", layout="wide")
    st.subheader("🧩 Phase E : Étape 4 : Les Modèles de Ressources (Templates)")

    # L'encart didactique a été déplacé dans le Cockpit (Concept).
    st.markdown("---")

    # INITIALISATION
    if "data_mcp" not in st.session_state:
        with st.spinner("Connexion au serveur 8002..."):
            try:
                res, tmpl = asyncio.run(mcp_discover_all())
                st.session_state.data_mcp = {"resources": res, "templates": tmpl}
                st.success("✅ Templates et Ressources récupérés !")
            except Exception as e:
                st.error(f"❌ Erreur de connexion : {e}")
                return

    # COLONNES D'INTERACTION
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("🔍 Explorer")
        
        # A. Ressources Statiques
        st.subheader("Fiches de synthèse (Statiques)")
        for r in st.session_state.data_mcp["resources"]:
            if st.button(f"📄 {r.name}", key=r.uri):
                st.session_state.view_uri = r.uri
        
        st.divider()
        
        # B. Templates
        st.subheader("Accès aux fiches détaillées (Templates)")
        for t in st.session_state.data_mcp["templates"]:
            with st.form(key=f"form_{t.name}"):
                st.write(f"**{t.name}**")
                st.caption(t.description)
                
                # On simule l'extraction du nom du paramètre (simplifié)
                param_name = "name" if "heroes" in t.uriTemplate else "title"
                val = st.text_input(f"Identifiant ({param_name})", placeholder="ex: thor")
                
                if st.form_submit_button("Récupérer"):
                    # On construit l'URI finale à partir du template
                    final_uri = t.uriTemplate.replace(f"{{{param_name}}}", val.strip())
                    st.session_state.view_uri = final_uri

    with col2:
        st.header("📄 Contenu de la ressource")
        if "view_uri" in st.session_state:
            uri = st.session_state.view_uri
            st.info(f"Lecture de l'URI : `{uri}`")
            try:
                content = asyncio.run(mcp_read(uri))
                st.text_area("Données récupérées", value=content, height=400)
            except Exception as e:
                st.error(f"Erreur : {e}")
                st.warning("Vérifiez l'identifiant saisi (doit correspondre au nom du fichier sans préfixe).")
        else:
            st.write("Sélectionnez une ressource ou remplissez un modèle à gauche.")

if __name__ == "__main__":
    main()
