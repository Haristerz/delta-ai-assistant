import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Delta AI Assistant",
    page_icon="✈️",
    layout="centered",
)

# ── Session state defaults ────────────────────────────────────────────────────

if "token"    not in st.session_state: st.session_state.token    = None
if "customer" not in st.session_state: st.session_state.customer = None
if "messages" not in st.session_state: st.session_state.messages = []

# ── Helpers ───────────────────────────────────────────────────────────────────

def login(email: str, password: str):
    response = requests.post(
        f"{API_BASE}/auth/login",
        data={"username": email, "password": password},
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def get_profile(token: str):
    response = requests.get(
        f"{API_BASE}/profile/",
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code == 200:
        return response.json()
    return None


def send_message(token: str, message: str):
    response = requests.post(
        f"{API_BASE}/chat/",
        json={"message": message},
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code == 200:
        return response.json()
    return None

# ── Login Page ────────────────────────────────────────────────────────────────

def show_login():
    st.title("✈️ Delta Air Lines")
    st.subheader("AI Customer Assistant")
    st.divider()

    with st.form("login_form"):
        email    = st.text_input("Email", placeholder="hari@delta.com")
        password = st.text_input("Password", type="password")
        submit   = st.form_submit_button("Login", use_container_width=True)

    if submit:
        if not email or not password:
            st.error("Please enter both email and password.")
            return

        with st.spinner("Logging in..."):
            token = login(email, password)

        if token:
            st.session_state.token = token
            profile = get_profile(token)
            if profile:
                st.session_state.customer = profile
            st.rerun()
        else:
            st.error("Incorrect email or password. Please try again.")

    st.divider()
    st.caption("Demo accounts: hari@delta.com / hari123  |  priya@delta.com / priya123")

# ── Chat Page ─────────────────────────────────────────────────────────────────

def show_chat():
    customer = st.session_state.customer

    with st.sidebar:
        st.title("✈️ Delta AI")
        st.divider()
        st.markdown(f"**{customer['name']}**")
        st.markdown(f"Tier: `{customer['tier']}`")
        st.markdown(f"Miles: `{customer['miles_balance']:,.0f}`")
        st.markdown(f"Member since: `{customer['member_since']}`")
        st.divider()

        if st.button("Logout", use_container_width=True):
            st.session_state.token    = None
            st.session_state.customer = None
            st.session_state.messages = []
            st.rerun()

    st.title("Delta AI Assistant")
    st.caption("Ask me about your miles, baggage, upgrades, or account.")
    st.divider()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Type your question here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = send_message(st.session_state.token, user_input)

            if result:
                reply = result["reply"]
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                st.error("Something went wrong. Please try again.")

# ── Main ──────────────────────────────────────────────────────────────────────

if st.session_state.token is None:
    show_login()
else:
    show_chat()
