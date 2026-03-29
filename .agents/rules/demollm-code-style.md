---
trigger: always_on
---

# Antigravity Custom Rules for Demo LLM Project

When working on the Demo LLM project, strictly adhere to the following architectural, pedagogical, and stylistic rules. This project prioritizes teaching value and transparent code over traditional software engineering patterns like DRY.

## 1. Pedagogical Clarity (Zero Over-Engineering)
- **Standalone Scripts**: Every Python demo file (e.g., `G03...`, `A01...`) MUST be entirely autonomous. Do not create complex central utility libraries or abstract base classes.
- **Embrace Duplication (Anti-DRY)**: Actively duplicate repetitive code (like `ChatOpenAI` instantiation or Streamlit UI headers) so that a learner can read a single file from top to bottom and understand the entire flow without navigating multiple files.

## 2. Monolithic File Structure
- **Two Distinct Sections**: Every UI demo script must be strictly separated into two visual sections using bold comments (e.g., `# -----------------`):
  1. **Section 1: Core Logic (Backend / LLM / LangChain / Tools)**. No Streamlit `st.` commands should exist here.
  2. **Section 2: User Interface (Streamlit)**. Handles user input, state (`st.session_state`), styling, and invokes the logic from Section 1.

## 3. Technology Stack Strictness
- **LLM Orchestration**: Strictly use `langchain` (and `langgraph` for complex loops).
- **User Interface**: Exclusively build interfaces using `streamlit`.
- **Interoperability**: Standardize tool orchestration through the `mcp` (Model Context Protocol) and multi-agent interaction via `google-adk` (Agent-to-Agent).

## 4. Configuration & Deployment
- **Environment Variables Only**: NEVER hardcode LLM models or API parameters. Always use `dotenv` and fetch values via `os.getenv("LLM_MODEL")`, `os.getenv("LLM_API_KEY")`, and `os.getenv("LLM_BASE_URL")`.
- **Cockpit Integration**: Ensure any new standalone Streamlit app is integrated into the central `00_demo_cockpit.py` orchestration hub (via `st.Page` for single processes, or via HTML `iframes` if complex underlying servers/agents are required).

## 5. Radical Transparency & Observability ("Show, Don't Tell")
- **Verbose Emoji Logging**: The Python backend must be highly chatty in the console. Liberally use `print()` statements tagged with easily identifiable emojis (e.g., `[ORCHESTRATOR] 📡`, `[AVENGERS] ⚡`, `[INFO CENTER] 📩`, `[TRACE] 🛡️`) so the demo audience can visualize the invisible backend.
- **Audit Trails**: Never hide the "AI Magic". Expose raw JSON payloads, Tool Calls, and trace IDs directly in the UI using Streamlit expanders (`st.expander()`) so users can inspect exactly what data the LLM interacted with.
