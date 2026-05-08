import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SWS AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 0 !important; }

.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    min-height: 100vh;
}
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.03) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}

/* Logo */
.sws-logo {
    display: flex; align-items: center; gap: 12px;
    padding: 1rem 1.2rem;
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(168,85,247,0.15));
    border-radius: 16px; border: 1px solid rgba(99,102,241,0.3);
    margin-bottom: 1.5rem;
}
.sws-logo .logo-icon { font-size: 2rem; }
.sws-logo .logo-text { color: #e2e8f0; font-size: 1.1rem; font-weight: 700; line-height: 1.2; }
.sws-logo .logo-sub  { color: rgba(255,255,255,0.45); font-size: 0.72rem; }

/* Inputs */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important; color: #e2e8f0 !important;
    padding: 0.75rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(99,102,241,0.7) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}
.stTextInput label { color: rgba(255,255,255,0.7) !important; font-size:0.85rem !important; font-weight:500 !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    padding: 0.7rem 1.5rem !important; font-weight: 600 !important;
    width: 100% !important; transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 8px 25px rgba(99,102,241,0.45) !important; }

/* Chat header */
.chat-header {
    background: rgba(255,255,255,0.03); border-bottom: 1px solid rgba(255,255,255,0.07);
    padding: 1rem 1.5rem; margin-bottom: 1rem; border-radius: 16px 16px 0 0;
    display: flex; align-items: center; justify-content: space-between;
}
.chat-header-title { color: #e2e8f0; font-size: 1rem; font-weight: 600; }
.chat-header-sub   { color: rgba(255,255,255,0.4); font-size: 0.78rem; }
.online-dot {
    width: 8px; height: 8px; background: #22c55e; border-radius: 50%;
    display: inline-block; margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%  { box-shadow: 0 0 0 0   rgba(34,197,94,0.4); }
    70% { box-shadow: 0 0 0 6px rgba(34,197,94,0);   }
    100%{ box-shadow: 0 0 0 0   rgba(34,197,94,0);   }
}

/* Bubbles */
.user-bubble       { display:flex; justify-content:flex-end; margin-bottom:1.2rem; }
.user-bubble-inner {
    background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white;
    padding: 0.9rem 1.2rem; border-radius: 18px 18px 4px 18px; max-width: 72%;
    font-size: 0.92rem; line-height: 1.6; box-shadow: 0 4px 15px rgba(99,102,241,0.3);
}
.ai-bubble       { display:flex; justify-content:flex-start; margin-bottom:1.2rem; gap:10px; align-items:flex-start; }
.ai-avatar       {
    width:34px; height:34px;
    background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(168,85,247,0.3));
    border: 1px solid rgba(99,102,241,0.4); border-radius:50%;
    display:flex; align-items:center; justify-content:center; font-size:0.9rem; flex-shrink:0;
}
.ai-bubble-inner {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    color: #e2e8f0; padding: 0.9rem 1.2rem; border-radius: 4px 18px 18px 18px;
    max-width: 72%; font-size: 0.92rem; line-height: 1.7; backdrop-filter: blur(10px);
}
.source-tag {
    display:inline-block; background:rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.3);
    color:rgba(99,102,241,0.9); border-radius:6px; padding:2px 8px;
    font-size:0.72rem; margin-top:8px; margin-right:4px;
}

/* Sidebar */
.sidebar-divider { height:1px; background:rgba(255,255,255,0.07); margin:1.2rem 0; }
.sidebar-label   { color:rgba(255,255,255,0.35); font-size:0.7rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.7rem; }
.info-card       { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:0.8rem 1rem; margin-bottom:0.5rem; color:#e2e8f0; font-size:0.82rem; }
.info-card span  { color:rgba(255,255,255,0.4); font-size:0.72rem; display:block; }

/* Welcome */
.welcome-container {
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    height:55vh; text-align:center; gap:1.5rem;
}
.welcome-icon  { font-size:3.5rem; }
.welcome-title { color:#f1f5f9; font-size:1.8rem; font-weight:700; }
.welcome-sub   { color:rgba(255,255,255,0.45); font-size:0.95rem; max-width:420px; line-height:1.6; }

/* Name form */
.name-card {
    background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1);
    border-radius:20px; padding:2.5rem; max-width:400px; margin:5rem auto;
    backdrop-filter:blur(20px);
}
.name-title { color:#f1f5f9; font-size:1.6rem; font-weight:700; text-align:center; margin-bottom:0.4rem; }
.name-sub   { color:rgba(255,255,255,0.45); font-size:0.88rem; text-align:center; margin-bottom:2rem; }
</style>
""", unsafe_allow_html=True)


# ─── Session State ────────────────────────────────────────────────────────────
for k, v in {
    "user_email": None,
    "messages": [],
    "session_id": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Backend Call ─────────────────────────────────────────────────────────────
def query_backend(question: str, session_id=None):
    try:
        payload = {
            "query": question,
            "user_email": st.session_state.user_email or "guest@sws.ai",
        }
        if session_id:
            payload["session_id"] = session_id

        resp = requests.post(
            f"{BACKEND_URL}/chat",
            json=payload,
            timeout=90
        )

        if resp.status_code == 200:
            data = resp.json()
            return data["answer"], data.get("sources", []), data.get("session_id")
        else:
            return f"⚠️ Backend error ({resp.status_code}): {resp.text}", [], None

    except requests.exceptions.ConnectionError:
        return "⚠️ Cannot reach the backend. Make sure Uvicorn is running on port 8000.", [], None
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}", [], None


# ─── Entry Screen ─────────────────────────────────────────────────────────────
def render_entry():
    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.markdown("""
        <div class="name-card">
            <div style="text-align:center; font-size:2.8rem; margin-bottom:1rem;">🤖</div>
            <div class="name-title">SWS AI Assistant</div>
            <div class="name-sub">Enter your name or email to start chatting with the company policy assistant.</div>
        </div>
        """, unsafe_allow_html=True)

        name = st.text_input("Your name or email", placeholder="e.g. john or john@company.com", key="entry_name")
        if st.button("Start Chatting →", key="btn_start"):
            if name.strip():
                # If they typed just a name, convert to a pseudo-email
                val = name.strip()
                if "@" not in val:
                    val = f"{val.lower().replace(' ', '.')}@sws.ai"
                st.session_state.user_email = val
                st.rerun()
            else:
                st.warning("Please enter your name or email to continue.")


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sws-logo">
            <div class="logo-icon">🤖</div>
            <div>
                <div class="logo-text">SWS AI</div>
                <div class="logo-sub">Intelligent Policy Assistant</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-card">
            👤 {st.session_state.user_email}
            <span>Active user</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕  New Conversation", key="new_chat"):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        if st.session_state.session_id:
            st.markdown('<div class="sidebar-label">Current Session</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="info-card">
                💬 Session #{st.session_state.session_id}
                <span>{len(st.session_state.messages)} messages</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-label">AI Stack</div>', unsafe_allow_html=True)
        for item in ["🧠 Gemini 2.5 Flash", "📚 Hybrid RAG", "🗄️ PostgreSQL + FAISS", "🔍 Semantic Memory"]:
            st.markdown(f'<div class="info-card">{item}</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        if st.button("🚪  Change User", key="logout_btn"):
            st.session_state.user_email = None
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()


# ─── Chat Page ────────────────────────────────────────────────────────────────
def render_chat():
    render_sidebar()

    st.markdown(f"""
    <div class="chat-header">
        <div>
            <div class="chat-header-title">
                <span class="online-dot"></span>Company Policy Assistant
            </div>
            <div class="chat-header-sub">Hybrid RAG · Gemini 2.5 Flash · Persistent Memory</div>
        </div>
        <div style="color:rgba(255,255,255,0.3); font-size:0.78rem;">
            Session: {st.session_state.session_id or "—"}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-container">
            <div class="welcome-icon">✨</div>
            <div class="welcome-title">What can I help you with?</div>
            <div class="welcome-sub">Ask me anything about company policies, leave rules, HR procedures, or any topic in our knowledge base.</div>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="user-bubble">
                <div class="user-bubble-inner">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            sources_html = ""
            for s in msg.get("sources", []):
                if s and s != "Unknown":
                    sources_html += f'<span class="source-tag">📄 {s}</span>'
            st.markdown(f"""
            <div class="ai-bubble">
                <div class="ai-avatar">🤖</div>
                <div class="ai-bubble-inner">
                    {msg["content"]}
                    {"<br>" + sources_html if sources_html else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)

    user_input = st.chat_input("Ask about leave policies, working hours, HR procedures...")

    if user_input and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})

        with st.spinner("🧠 Thinking..."):
            answer, sources, new_sid = query_backend(user_input.strip(), st.session_state.session_id)

        if new_sid and not st.session_state.session_id:
            st.session_state.session_id = new_sid

        st.session_state.messages.append({"role": "ai", "content": answer, "sources": sources})
        st.rerun()


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.user_email:
        render_entry()
    else:
        render_chat()

if __name__ == "__main__":
    main()
