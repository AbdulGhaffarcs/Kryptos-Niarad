import streamlit as st
import os
@st.cache_resource
def get_system_engine():
    """
    Imports heavy modules ONLY when needed and keeps them in RAM.
    """
    from core.loaders import load_file_dynamically, get_chunks
    from core.vector_store import add_to_store, get_vector_store
    from core.logic_engine import route_query, get_rag_chain
    return {
        "loader": load_file_dynamically,
        "splitter": get_chunks,
        "vault": add_to_store,
        "db": get_vector_store,
        "router": route_query,
        "chain_gen": get_rag_chain
    }

# --- PAGE CONFIG ---
st.set_page_config(page_title="Vault-X | AI Command Center", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS FOR THE HOME SCREEN ---
st.markdown("""
    <style>
    .main-title { font-size: 50px; font-weight: 700; color: #00FFAA; text-align: center; margin-bottom: 0px; }
    .sub-text { font-size: 20px; text-align: center; color: #888; margin-bottom: 50px; }
    .feature-card { background-color: #1E1E1E; border-radius: 10px; padding: 20px; border: 1px solid #333; height: 100%; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #00FFAA; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "chat_active" not in st.session_state:
    st.session_state.chat_active = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR (Always Visible) ---
with st.sidebar:
    st.title("🛡️ Vault Controls")
    uploaded_files = st.file_uploader("Upload Study Material", 
                                     type=["pdf", "docx", "pptx", "xlsx", "csv"], 
                                     accept_multiple_files=True)
    
    if st.button("Update Local Brain"):
        if uploaded_files:
            for f in uploaded_files:
                with st.spinner(f"Indexing {f.name}..."):
                    # Use your modular core functions
                    docs = load_file_dynamically(f.name) 
                    chunks = get_chunks(docs)
                    add_to_store(chunks)
            st.success("Vault Synchronized.")
    
    st.divider()
    if st.button("Clear Command History"):
        st.session_state.messages = []
        st.session_state.chat_active = False
        st.rerun()

# --- HOME SCREEN VIEW ---
if not st.session_state.get('chat_active', False):
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<h1 class='title-text'>NIARAD</h1>", unsafe_allow_html=True)
    st.markdown("<div class='status-tag'>OFFLINE SECURE // AI CORE ACTIVE</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""<div class='glass-card'>
            <h4 style='color:#00FFAA;'>📅 Extraction</h4>
            <p style='font-size:14px; color:#999;'>Parsing Sukkur IBA schedules. Automated mapping of venues and exam timelines.</p>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""<div class='glass-card'>
            <h4 style='color:#00FFAA;'>📚 Synthesis</h4>
            <p style='font-size:14px; color:#999;'>Abstracting IR and CS frameworks. Turning complex lectures into actionable insights.</p>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown("""<div class='glass-card'>
            <h4 style='color:#00FFAA;'>🛡️ Security</h4>
            <p style='font-size:14px; color:#999;'>Your assets remain air-gapped. Zero cloud telemetry for total research privacy.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1,1,1])
    with mid:
        if st.button("INITIALIZE INTERFACE"):
            st.session_state.chat_active = True
            st.rerun()

# --- CHAT INTERFACE VIEW ---
else:
    # System Handshake for Empty State
    if not st.session_state.messages:
        st.markdown("""
            <div style='margin-top: 15vh; text-align: center; padding: 40px; background: rgba(255,255,255,0.02); border-radius: 15px; border: 1px solid rgba(255,255,255,0.05);'>
                <div style='color: #00FFAA; font-family: monospace; font-size: 10px; letter-spacing: 4px; margin-bottom: 20px;'>[ SESSION INITIALIZED ]</div>
                <h2 style='font-weight: 100; letter-spacing: 15px; color: #FFF;'>NIARAD</h2>
                <p style='color: #555; font-size: 12px; font-style: italic; margin-top: 20px;'>"Information is the resolution of uncertainty."</p>
            </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Enter command..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# Processing the assistant reply (post-rerun to maintain speed)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    engine = get_system_engine()
    query = st.session_state.messages[-1]["content"]
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            mode = engine["router"](query)
            db = engine["db"]()
            chain = engine["chain_gen"](db.as_retriever(), mode)
            response = chain.invoke(query)
            st.markdown(f"**Mode: {mode}**\n\n{response}")
            st.session_state.messages.append({"role": "assistant", "content": response})