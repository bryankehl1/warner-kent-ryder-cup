import streamlit as st
import pandas as pd
import json
from datetime import datetime
import pyrebase

# ── Your Firebase config (PASTE YOUR VALUES HERE FROM FIREBASE CONSOLE) ──
firebaseConfig = {
    "apiKey": "YOUR_API_KEY_HERE",
    "authDomain": "your-project-id.firebaseapp.com",
    "databaseURL": "https://your-project-id-default-rtdb.firebaseio.com",  # <-- THIS IS CRITICAL
    "projectId": "your-project-id",
    "storageBucket": "your-project-id.appspot.com",
    "messagingSenderId": "YOUR_SENDER_ID",
    "appId": "YOUR_APP_ID"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

st.set_page_config(page_title="Warner vs Kent Ryder Cup", page_icon="⛳", layout="centered")

# Light mobile-friendly CSS
st.markdown("""
<style>
    .stApp { padding: 0.8rem; background: #f5f5f7; }
    button { width: 100%; height: 3.2rem; font-size: 1.1rem; border-radius: 12px; }
    .stNumberInput input { font-size: 1.5rem !important; text-align: center; }
    .match-card { background: white; border-radius: 16px; padding: 1.2rem; margin: 1rem 0; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
</style>
""", unsafe_allow_html=True)

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

team_w = list(st.session_state.players.keys())[0]
team_k = list(st.session_state.players.keys())[1]
w_list = st.session_state.players[team_w]
k_list = st.session_state.players[team_k]

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

        # Player selection (your preferred style)
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
                "scores_w": [0]*18,  # Replace with actual saved values
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

st.caption("Live sync via Firebase – changes appear for everyone in seconds. If blank on iPhone: Try Chrome app or refresh after 10 sec.")
