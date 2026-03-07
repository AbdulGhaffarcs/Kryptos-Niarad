import streamlit as st
import os
import tempfile
from core.logic_engine import FREE_TIER_LIMIT, is_small_talk

# ─────────────────────────────────────────────
#  ENGINE
# ─────────────────────────────────────────────
@st.cache_resource
def get_system_engine():
    from core.loaders import load_file_dynamically, get_chunks
    from core.vector_store import add_to_store, get_vector_store, clear_store
    from core.logic_engine import route_query, get_rag_chain, get_direct_chain, get_small_talk_chain
    return {
        "loader":             load_file_dynamically,
        "splitter":           get_chunks,
        "vault":              add_to_store,
        "db":                 get_vector_store,
        "clear":              clear_store,
        "router":             route_query,
        "chain_gen":          get_rag_chain,
        "direct_chain":       get_direct_chain,
        "small_talk_chain":   get_small_talk_chain,
    }

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="NIARAD | AI Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&display=swap');

/* ── Force dark everywhere ── */
html, body, [class*="css"], .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"],
section[data-testid="stSidebar"] > div,
.main .block-container {
    background-color: #080B0F !important;
    color: #C8D6E5 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
    background-color: #0D1117 !important;
    border-right: 1px solid #1C2A3A !important;
}
[data-testid="stSidebar"] * {
    color: #C8D6E5 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* ── All text ── */
p, h1, h2, h3, h4, h5, span, label, div {
    color: #C8D6E5 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid #00FFAA !important;
    color: #00FFAA !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 2px !important;
    border-radius: 2px !important;
    padding: 8px 16px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #00FFAA !important;
    color: #080B0F !important;
    box-shadow: 0 0 20px rgba(0,255,170,0.3) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #0D1117 !important;
    border: 1px dashed #1C2A3A !important;
    border-radius: 4px !important;
}
[data-testid="stFileUploader"] * { color: #C8D6E5 !important; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background-color: #0D1117 !important;
    border: 1px solid #1C2A3A !important;
    border-radius: 4px !important;
    margin-bottom: 8px !important;
}
[data-testid="stChatMessage"] * { color: #C8D6E5 !important; }

/* ── Chat input ── */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] textarea {
    background-color: #0D1117 !important;
    border: 1px solid #1C2A3A !important;
    border-radius: 2px !important;
    color: #C8D6E5 !important;
    font-family: 'Share Tech Mono', monospace !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #00FFAA !important;
    box-shadow: 0 0 12px rgba(0,255,170,0.15) !important;
    outline: none !important;
}
[data-testid="stChatInput"] button {
    background: #00FFAA !important;
    border: none !important;
    border-radius: 2px !important;
}
[data-testid="stChatInput"] button svg { color: #080B0F !important; fill: #080B0F !important; }

/* ── Divider ── */
hr { border-color: #1C2A3A !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #00FFAA !important; }

/* ── Progress bar ── */
.stProgress > div > div { background-color: #00FFAA !important; }

/* ── Alerts ── */
[data-testid="stAlert"] { background-color: #0D1117 !important; border-color: #1C2A3A !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #080B0F; }
::-webkit-scrollbar-thumb { background: #1C2A3A; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #00FFAA; }

/* ── Mode badges ── */
.mode-badge {
    display: inline-block !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    padding: 2px 10px !important;
    border-radius: 2px !important;
    margin-bottom: 10px !important;
}
.mode-extraction { background: rgba(0,200,255,0.12) !important; color: #00C8FF !important; border: 1px solid #00C8FF50 !important; }
.mode-summary    { background: rgba(0,255,170,0.12) !important; color: #00FFAA !important;  border: 1px solid #00FFAA50 !important; }
.mode-direct     { background: rgba(255,200,0,0.12) !important;  color: #FFC800 !important;  border: 1px solid #FFC80050 !important; }

/* ── Vault status ── */
.vault-active   { color: #00FFAA !important; font-family: 'Share Tech Mono', monospace !important; font-size: 11px !important; }
.vault-inactive { color: #FF4466 !important; font-family: 'Share Tech Mono', monospace !important; font-size: 11px !important; }

/* ── Tier bar ── */
.tier-bar-wrap {
    background: #0D1117 !important;
    border: 1px solid #1C2A3A !important;
    border-radius: 2px !important;
    height: 4px !important;
    width: 100% !important;
    margin: 6px 0 !important;
    overflow: hidden !important;
}
.tier-bar-fill { height: 100% !important; border-radius: 2px !important; transition: width 0.4s ease !important; }

/* ── Glass cards ── */
.glass-card {
    background: rgba(13,17,23,0.9) !important;
    border: 1px solid #1C2A3A !important;
    border-radius: 4px !important;
    padding: 24px !important;
    height: 100% !important;
}
.glass-card:hover { border-color: #00FFAA40 !important; }

/* ── Home ── */
.home-title {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 64px !important;
    font-weight: 400 !important;
    color: #FFFFFF !important;
    text-align: center !important;
    letter-spacing: 20px !important;
    margin: 0 !important;
    text-shadow: 0 0 60px rgba(0,255,170,0.15) !important;
}
.home-sub {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 6px !important;
    color: #00FFAA !important;
    text-align: center !important;
    margin-top: 8px !important;
}
.home-quote {
    font-size: 14px !important;
    color: #2A3A4A !important;
    text-align: center !important;
    font-style: italic !important;
    margin-top: 16px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "chat_active": False,
    "messages": [],
    "free_messages_used": 0,
    "vault_has_docs": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Check vault status on load
def refresh_vault_status():
    engine = get_system_engine()
    st.session_state.vault_has_docs = engine["db"]() is not None

refresh_vault_status()

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ VAULT CONTROLS")
    st.divider()

    # Vault status indicator
    if st.session_state.vault_has_docs:
        st.markdown('<span class="vault-active">◆ VAULT ONLINE</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="vault-inactive">◇ VAULT EMPTY</span>', unsafe_allow_html=True)

    # Free tier usage (only shown when vault is empty)
    if not st.session_state.vault_has_docs:
        used = st.session_state.free_messages_used
        remaining = max(0, FREE_TIER_LIMIT - used)
        pct = min(100, int((used / FREE_TIER_LIMIT) * 100))
        bar_color = "#00FFAA" if pct < 70 else "#FFC800" if pct < 90 else "#FF4466"
        st.markdown(f"""
        <div style='margin: 8px 0 4px;'>
            <span style='font-family:Share Tech Mono,monospace; font-size:10px; color:#3A4A5A;'>
                FREE TIER — {remaining}/{FREE_TIER_LIMIT} REMAINING
            </span>
        </div>
        <div class='tier-bar-wrap'>
            <div class='tier-bar-fill' style='width:{pct}%; background:{bar_color};'></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # File uploader
    uploaded_files = st.file_uploader(
        "Upload Study Material",
        type=["pdf", "docx", "pptx", "xlsx", "csv"],
        accept_multiple_files=True,
        help="PDF, DOCX, PPTX, XLSX, CSV supported"
    )

    if st.button("⬆ UPDATE LOCAL BRAIN"):
        if uploaded_files:
            engine = get_system_engine()
            progress = st.progress(0)
            errors = []
            for i, f in enumerate(uploaded_files):
                with st.spinner(f"Indexing {f.name}..."):
                    suffix = os.path.splitext(f.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(f.read())
                        tmp_path = tmp.name
                    try:
                        docs = engine["loader"](tmp_path)
                        chunks = engine["splitter"](docs)
                        engine["vault"](chunks)
                    except Exception as e:
                        errors.append(f"{f.name}: {str(e)}")
                    finally:
                        os.unlink(tmp_path)
                progress.progress((i + 1) / len(uploaded_files))
            progress.empty()
            if errors:
                for err in errors:
                    st.error(f"⚠ {err}")
            else:
                st.success("✓ Vault synchronized.")
            refresh_vault_status()
        else:
            st.warning("No files selected.")

    st.divider()

    if st.button("✕ CLEAR VAULT"):
        engine = get_system_engine()
        engine["clear"]()
        refresh_vault_status()
        st.success("Vault cleared.")

    if st.button("✕ CLEAR HISTORY"):
        st.session_state.messages = []
        st.session_state.free_messages_used = 0
        st.session_state.chat_active = False
        st.rerun()

    st.divider()
    st.markdown("""
    <div style='font-family:Share Tech Mono,monospace; font-size:9px; color:#1C2A3A; line-height:1.8;'>
    NIARAD v2.0<br>
    OFFLINE SECURE<br>
    ZERO TELEMETRY<br>
    LOCAL LLM ONLY
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HOME SCREEN
# ─────────────────────────────────────────────
if not st.session_state.chat_active:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p class='home-title'>NIARAD</p>", unsafe_allow_html=True)
    st.markdown("<p class='home-sub'>OFFLINE SECURE // AI CORE ACTIVE</p>", unsafe_allow_html=True)
    st.markdown("<p class='home-quote'>\"Information is the resolution of uncertainty.\"</p>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""<div class='glass-card'>
            <div style='font-family:Share Tech Mono,monospace; font-size:10px; color:#00C8FF; letter-spacing:3px; margin-bottom:12px;'>EXTRACTION</div>
            <p style='font-size:15px; color:#C8D6E5; margin:0 0 8px;'>Schedule & Data Mining</p>
            <p style='font-size:13px; color:#3A4A5A; margin:0;'>Parse exam timetables, venues, and specific facts from uploaded documents.</p>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""<div class='glass-card'>
            <div style='font-family:Share Tech Mono,monospace; font-size:10px; color:#00FFAA; letter-spacing:3px; margin-bottom:12px;'>SYNTHESIS</div>
            <p style='font-size:15px; color:#C8D6E5; margin:0 0 8px;'>Concept Intelligence</p>
            <p style='font-size:13px; color:#3A4A5A; margin:0;'>Turn complex lecture slides and notes into clear, structured summaries.</p>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown("""<div class='glass-card'>
            <div style='font-family:Share Tech Mono,monospace; font-size:10px; color:#FFC800; letter-spacing:3px; margin-bottom:12px;'>FREE TIER</div>
            <p style='font-size:15px; color:#C8D6E5; margin:0 0 8px;'>General AI Mode</p>
            <p style='font-size:13px; color:#3A4A5A; margin:0;'>Chat with NIARAD without uploading files. Up to {limit} free messages per session.</p>
        </div>""".format(limit=FREE_TIER_LIMIT), unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        if st.button("INITIALIZE INTERFACE"):
            st.session_state.chat_active = True
            st.rerun()

# ─────────────────────────────────────────────
#  CHAT INTERFACE
# ─────────────────────────────────────────────
else:
    # Empty state header
    if not st.session_state.messages:
        vault_status = "◆ VAULT ONLINE — Document-aware mode active." if st.session_state.vault_has_docs \
            else f"◇ VAULT EMPTY — General mode active. {FREE_TIER_LIMIT} free messages available."
        status_color = "#00FFAA" if st.session_state.vault_has_docs else "#FFC800"

        st.markdown(f"""
        <div style='margin-top:12vh; text-align:center; padding:48px 32px;
                    background:rgba(13,17,23,0.6); border-radius:4px;
                    border:1px solid #1C2A3A;'>
            <div style='font-family:Share Tech Mono,monospace; font-size:9px;
                        letter-spacing:5px; color:{status_color}; margin-bottom:24px;'>
                [ SESSION INITIALIZED ]
            </div>
            <h2 style='font-family:Share Tech Mono,monospace; font-weight:400;
                       letter-spacing:16px; color:#FFF; margin:0;'>NIARAD</h2>
            <p style='font-family:Share Tech Mono,monospace; font-size:10px;
                      color:{status_color}; margin-top:16px; letter-spacing:2px;'>
                {vault_status}
            </p>
            <p style='color:#2A3A4A; font-size:12px; font-style:italic; margin-top:20px;'>
                "Information is the resolution of uncertainty."
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Render message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)

    # Determine if free tier is exhausted
    free_exhausted = (
        not st.session_state.vault_has_docs
        and st.session_state.free_messages_used >= FREE_TIER_LIMIT
    )

    if free_exhausted:
        st.warning(
            f"⚠ Free tier limit reached ({FREE_TIER_LIMIT} messages). "
            "Upload documents via the sidebar to continue with full access."
        )

    # Chat input
    chat_placeholder = (
        "Enter command..." if st.session_state.vault_has_docs
        else f"Free mode — {max(0, FREE_TIER_LIMIT - st.session_state.free_messages_used)} messages left..."
    )

    if prompt := st.chat_input(chat_placeholder, disabled=free_exhausted):
        # Append and render user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        engine = get_system_engine()
        db = engine["db"]()

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    if is_small_talk(prompt):
                        # ── SMALL TALK — fastest path, no routing, no retrieval ──
                        chain = engine["small_talk_chain"]()
                        response = chain.invoke(prompt)
                        st.markdown(
                            "<span class='mode-badge mode-direct'>NIARAD</span>",
                            unsafe_allow_html=True
                        )
                        st.markdown(response)
                        full_response = response

                    elif db is not None:
                        # ── RAG MODE ──
                        mode = engine["router"](prompt)
                        chain = engine["chain_gen"](db.as_retriever(), mode)
                        response = chain.invoke(prompt)
                        badge_class = "mode-extraction" if mode == "EXTRACTION" else "mode-summary"
                        st.markdown(
                            f"<span class='mode-badge {badge_class}'>{mode}</span>",
                            unsafe_allow_html=True
                        )
                        st.markdown(response)
                        full_response = f"**[{mode}]**\n\n{response}"

                    else:
                        # ── FREE / DIRECT MODE ──
                        st.session_state.free_messages_used += 1
                        remaining = FREE_TIER_LIMIT - st.session_state.free_messages_used
                        chain = engine["direct_chain"]()
                        response = chain.invoke(prompt)
                        st.markdown(
                            "<span class='mode-badge mode-direct'>GENERAL MODE</span>",
                            unsafe_allow_html=True
                        )
                        st.markdown(response)
                        if remaining > 0:
                            st.caption(f"🔓 {remaining} free messages remaining. Upload docs for full document-aware answers.")
                        else:
                            st.warning("⚠ Free tier limit reached. Upload documents to continue.")
                        full_response = response

                except Exception as e:
                    full_response = f"⚠ Error: {str(e)}"
                    st.error(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})