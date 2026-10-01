"""Login / Register landing page (app.py → Entry point)."""

import streamlit as st
from ui_utils import HIDE_STREAMLIT_CHROME

from db import login_user, register_user

st.set_page_config(
    page_title="ShopReturn AI",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Hide white header bar
st.markdown(HIDE_STREAMLIT_CHROME, unsafe_allow_html=True)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        min-height: 100vh;
    }

    /* Card wrapper */
    .auth-card {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.14);
        backdrop-filter: blur(18px);
        border-radius: 24px;
        padding: 2.5rem 2rem;
        max-width: 440px;
        margin: 3rem auto 0;
    }

    .auth-title {
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: .25rem;
    }

    .auth-sub {
        text-align: center;
        color: rgba(255,255,255,0.55);
        font-size: .95rem;
        margin-bottom: 2rem;
    }

    /* Inputs */
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 12px !important;
        color: #fff !important;
        font-size: 1rem !important;
        padding: .6rem 1rem !important;
    }

    div[data-baseweb="input"] input:focus,
    div[data-baseweb="base-input"] input:focus {
        border-color: #a78bfa !important;
        box-shadow: 0 0 0 3px rgba(167,139,250,0.25) !important;
    }

    label[data-testid="stWidgetLabel"] p { color: rgba(255,255,255,0.75) !important; font-size: .9rem; }

    /* Primary button */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #7c3aed, #2563eb) !important;
        border: none !important;
        border-radius: 14px !important;
        padding: .7rem 1.5rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #fff !important;
        width: 100%;
        transition: transform .15s, box-shadow .15s;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(124,58,237,.45) !important;
    }

    /* Secondary button */
    div.stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 14px !important;
        color: rgba(255,255,255,0.8) !important;
        width: 100%;
        font-size: .95rem;
    }

    div[data-testid="stTabs"] button { color: rgba(255,255,255,0.65) !important; font-weight: 500; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color: #a78bfa !important; }

    /* Alert colours */
    div[data-testid="stAlert"] { border-radius: 12px; }

    /* Hide sidebar nav labels for a cleaner look */
    section[data-testid="stSidebarNav"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Redirect if already logged in ───────────────────────────────────────────
if st.session_state.get("user"):
    st.switch_page("pages/1_🛒_Shop.py")

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center; padding-top: 2.5rem;">
      <div style="font-size:3.5rem;">🛍️</div>
      <div class="auth-title">ShopReturn AI</div>
      <div class="auth-sub">Smart shopping · Seamless returns · AI-powered decisions</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Auth Tabs ────────────────────────────────────────────────────────────────
tab_login, tab_reg = st.tabs(["🔑  Sign In", "✨  Create Account"])

with tab_login:
    st.write("")
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="your_username")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Sign In", type="primary")

    if submitted:
        if not username or not password:
            st.error("Please fill in all fields.")
        else:
            with st.spinner("Authenticating…"):
                user = login_user(username.strip(), password)
            if user:
                st.session_state["user"] = user
                st.session_state["cart"] = {}
                st.success(f"Welcome back, {user['full_name']}! 🎉")
                st.switch_page("pages/1_🛒_Shop.py")
            else:
                st.error("Invalid username or password.")

with tab_reg:
    st.write("")
    with st.form("register_form"):
        r_full  = st.text_input("Full Name",  placeholder="Aarav Sharma", key="r_full")
        r_email = st.text_input("Email",      placeholder="aarav@example.com", key="r_email")
        r_user  = st.text_input("Username",   placeholder="aarav123", key="r_user")
        r_pass  = st.text_input("Password",   type="password", placeholder="Min 6 characters", key="r_pass")
        r_sub   = st.form_submit_button("Create Account", type="primary")

    if r_sub:
        if not all([r_full, r_email, r_user, r_pass]):
            st.error("Please fill in all fields.")
        elif len(r_pass) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            with st.spinner("Creating your account…"):
                result = register_user(r_user.strip(), r_email.strip(), r_pass, r_full.strip())
            if result["ok"]:
                st.success("Account created! Please sign in.")
            else:
                st.error(result["error"])

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center; margin-top:3rem; color:rgba(255,255,255,0.3); font-size:.8rem;">
      Class demo · MongoDB · LangChain · LangGraph · OpenRouter AI
    </div>
    """,
    unsafe_allow_html=True,
)
