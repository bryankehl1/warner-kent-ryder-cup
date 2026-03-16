import streamlit as st
import pandas as pd
import json
from datetime import datetime
import pyrebase

# ── Your Firebase config (already correct from your paste) ──
firebaseConfig = {
    "apiKey": "AIzaSyBHxFmZYsVSm4clbXpE4u-1LFZSW8Mg5CE",
    "authDomain": "warner-kent-ryder-cup.firebaseapp.com",
    "databaseURL": "https://warner-kent-ryder-cup-default-rtdb.firebaseio.com",
    "projectId": "warner-kent-ryder-cup",
    "storageBucket": "warner-kent-ryder-cup.firebasestorage.app",
    "messagingSenderId": "364132704196",
    "appId": "1:364132704196:web:4348ae83bb93eb1ecf8e91"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# ── High-contrast mobile-friendly CSS (fixes white-on-white) ──
st.markdown("""
<style>
    /* Force readable colors & safe mobile base */
    body, .stApp, .block-container {
        background-color: #f8f9fa !important;  /* light gray-white */
        color: #1a1a1a !important;             /* near-black text */
    }
    h1, h2, h3, p, label, div, span, .stMarkdown {
        color: #1a1a1a !important;
    }
    button, .stButton > button {
        background-color: #0066cc !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        height: 3.2rem !important;
        width: 100% !important;
        margin: 0.6rem 0 !important;
    }
    button:hover {
        background-color: #0052a3 !important;
    }
    .stNumberInput input {
        font-size: 1.5rem !important;
        text-align: center !important;
        color: #000000 !important;
        background: white !important;
        border: 1px solid #ccc !important;
        border-radius: 8px !important;
    }
    .match-card {
        background: white !important;
        border-radius: 16px !important;
        padding: 1.2rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.1) !important;
        border: 1px solid #e0e0e0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #1a1a1a !important;
        font-size: 1.05rem !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #e6f0ff !important;
        color: #0066cc !important;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Warner vs Kent Ryder Cup", page_icon="⛳", layout="centered")

st.title("Warner vs Kent Ryder Cup")

# ── Load from Firebase on start ──
@st.cache_data(ttl=10)  # Refresh every 10 sec
def load_from_firebase():
    try:
        data = db.get().val() or {}
        st.session_state.players = data.get("players", st.session_state.get("players", {}))
        st.session_state.matches = data.get("matches", st.session_state.get("matches", {}))
        st.session_state.player_points = data.get("player_points", st.session_state.get("player_points", {}))
    except Exception as e:
        st.warning(f"Firebase load failed: {e}. Using local state.")

load_from_firebase()

# ── Players (sidebar) ──
with st.sidebar:
    st.header("Teams & Players")
    team_w = st.text_input("Team Warner", "Team Warner")
    team_k = st.text_input("Team Kent", "Team Kent")
    w_players = [st.text_input(f"Player {i+1}", st.session_state.players.get(team_w, [""]*4)[i], key=f"wp_{i}") for i in range(4)]
    k_players = [st.text_input(f"Player {i+1}", st.session_state.players.get(team_k, [""]*4)[i], key=f"kp_{i}") for i in range(4)]

    if st.button("Save Players"):
        st.session_state.players = {team_w: w_players, team_k: k_players}
        db.child("players").set(st.session_state.players)
        st.success("Players saved & synced!")
        st.rerun()

# Get team names safely – fallback if empty
players_dict = st.session_state.get("players", {})
if players_dict:
    team_w = list(players_dict.keys())[0]
    team_k = list(players_dict.keys())[1] if len(players_dict) > 1 else "Team Kent"
    w_list = players_dict.get(team_w, ["Player W1", "Player W2", "Player W3", "Player W4"])
    k_list = players_dict.get(team_k, ["Player K1", "Player K2", "Player K3", "Player K4"])
else:
    team_w = "Team Warner"
    team_k = "Team Kent"
    w_list = ["Player W1", "Player W2", "Player W3", "Player W4"]
    k_list = ["Player K1", "Player K2", "Player K3", "Player K4"]
    st.session_state.players = {team_w: w_list, team_k: k_list}

# ── Tabs at top ──
tab_setup, tab_scores, tab_lb, tab_pp = st.tabs(["Setup", "Enter Scores", "Leaderboard", "Player Points"])

with tab_setup:
    st.subheader("Create Matches")
    if st.button("🚀 Create All 10 Matches", use_container_width=True):
        for r, fmt, cnt in [("R1","Foursomes",2), ("R2","Fourball",2), ("R3","Greensomes",2), ("R4","Singles",4)]:
            for m in range(1, cnt+1):
                key = f"{r}-M{m}"
                st.session_state.matches[key] = {
                    "format": fmt,
                    "players_w": w_list[:2] if fmt != "Singles" else [w_list[0]],
                    "players_k": k_list[:2] if fmt != "Singles" else [k_list[0]],
                    "scores_w": [0]*18,
                    "scores_k": [0]*18,
                    "ind_w": [0]*18 if fmt=="Singles" else None,
                    "ind_k": [0]*18 if fmt=="Singles" else None,
                    "pts_w": 0.0,
                    "pts_k": 0.0
                }
        db.child("matches").set(st.session_state.matches)
        st.success("Matches created & synced!")
        st.rerun()

with tab_scores:
    st.subheader("Enter Scores")
    match_keys = list(st.session_state.matches.keys())
    if not match_keys:
        st.info("No matches yet – create in Setup tab")
    else:
        selected_key = st.selectbox("Select Match", match_keys, format_func=lambda k: f"{k} – {st.session_state.matches[k]['format']}")
        m = st.session_state.matches[selected_key]

        # Player selection
        if m["format"] == "Singles":
            pw = st.selectbox("Warner Player", w_list, key=f"pw_{selected_key}")
            pk = st.selectbox("Kent Player", k_list, key=f"pk_{selected_key}")
        else:
            pw = st.multiselect("Warner Pair", w_list, default=m.get("players_w", []), max_selections=2, key=f"mpw_{selected_key}")
            pk = st.multiselect("Kent Pair", k_list, default=m.get("players_k", []), max_selections=2, key=f"mpk_{selected_key}")

        # Per-hole numeric input
        for h in range(18):
            col_h, col_w, col_k = st.columns([1, 3, 3])
            col_h.write(f"**Hole {h+1}**")
            sw = col_w.number_input(" ", min_value=0, step=1, value=0, key=f"sw_{selected_key}_{h}", label_visibility="collapsed")
            sk = col_k.number_input(" ", min_value=0, step=1, value=0, key=f"sk_{selected_key}_{h}", label_visibility="collapsed")

        if st.button("💾 Save & Calculate Match", use_container_width=True, key=f"save_{selected_key}"):
            # Update session state (you can add point calc logic here)
            db.child("matches").child(selected_key).update({
                "scores_w": [0]*18,  # ← Replace with actual saved values from inputs
                "scores_k": [0]*18
            })
            st.success("Match saved & synced to cloud!")
            st.rerun()

# Leaderboard
with tab_lb:
    total_w = sum(m.get("pts_w", 0) for m in st.session_state.matches.values())
    total_k = sum(m.get("pts_k", 0) for m in st.session_state.matches.values())
    st.metric(team_w, f"{total_w:.1f}")
    st.metric(team_k, f"{total_k:.1f}")

# Player Points
with tab_pp:
    df = pd.DataFrame(list(st.session_state.player_points.items()), columns=["Player", "Points"]).sort_values("Points", ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)

st.caption("Live sync via Firebase – changes appear for everyone in seconds. If text still faint: Try Chrome app on iPhone.")
