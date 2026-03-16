import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Force better mobile viewport scaling
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)

# Light mobile CSS only (no heavy overrides)
st.markdown("""
<style>
    .stApp { padding: 1rem; }
    button { width: 100%; height: 3rem; font-size: 1.1rem; margin: 0.5rem 0; }
    .stNumberInput input { font-size: 1.4rem; text-align: center; }
    .match-card { background: #fff; border-radius: 12px; padding: 1rem; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Warner vs Kent Ryder Cup", page_icon="⛳", layout="centered")  # Changed from wide

# Session init (same as before)
if 'players' not in st.session_state:
    st.session_state.players = {"Team Warner": ["Player W1", "Player W2", "Player W3", "Player W4"], "Team Kent": ["Player K1", "Player K2", "Player K3", "Player K4"]}
if 'matches' not in st.session_state:
    st.session_state.matches = {}
if 'player_points' not in st.session_state:
    st.session_state.player_points = {}

st.title("Warner vs Kent Ryder Cup")

# Sync section
with st.expander("Sync / Backup Tournament"):
    if st.button("Generate JSON (copy this)"):
        export = {"players": st.session_state.players, "matches": st.session_state.matches, "player_points": st.session_state.player_points}
        st.code(json.dumps(export, indent=2), language="json")
    paste = st.text_area("Paste previous JSON here to restore")
    if st.button("Load Pasted JSON") and paste:
        try:
            data = json.loads(paste)
            st.session_state.players = data.get("players", st.session_state.players)
            st.session_state.matches = data.get("matches", {})
            st.session_state.player_points = data.get("player_points", {})
            st.rerun()
        except:
            st.error("Invalid JSON")

# Players
with st.expander("Teams & Players"):
    team_w = st.text_input("Team Warner", "Team Warner")
    team_k = st.text_input("Team Kent", "Team Kent")
    w_players = [st.text_input(f"P{i+1}", st.session_state.players.get(team_w, [""]*4)[i], key=f"wp{i}") for i in range(4)]
    k_players = [st.text_input(f"P{i+1}", st.session_state.players.get(team_k, [""]*4)[i], key=f"kp{i}") for i in range(4)]
    if st.button("Save Players"):
        st.session_state.players = {team_w: w_players, team_k: k_players}
        st.rerun()

team_w = list(st.session_state.players.keys())[0]
team_k = list(st.session_state.players.keys())[1]
w_list = st.session_state.players[team_w]
k_list = st.session_state.players[team_k]

# Tabs (simplified)
tab_setup, tab_scores = st.tabs(["Setup Matches", "Enter Scores"])

with tab_setup:
    if st.button("Create All 10 Matches"):
        for r, fmt, cnt in [("R1","Foursomes",2), ("R2","Fourball",2), ("R3","Greensomes",2), ("R4","Singles",4)]:
            for m in range(1, cnt+1):
                key = f"{r}-M{m}"
                st.session_state.matches[key] = {"format": fmt, "players_w": w_list[:2 if fmt != "Singles" else 1], "players_k": k_list[:2 if fmt != "Singles" else 1], "scores_w": [0]*18, "scores_k": [0]*18, "pts_w": 0.0, "pts_k": 0.0}
        st.rerun()

with tab_scores:
    round_sel = st.selectbox("Round", ["Round 1 – Foursomes", "Round 2 – Fourball", "Round 3 – Greensomes", "Round 4 – Singles"])
    r_key = {"Round 1":"R1", "Round 2":"R2", "Round 3":"R3", "Round 4":"R4"}[round_sel.split(" – ")[0]]

    for i in range(1, 5 if "Singles" in round_sel else 3):
        key = f"{r_key}-M{i}"
        if key in st.session_state.matches:
            with st.container():
                st.markdown('<div class="match-card">', unsafe_allow_html=True)
                st.subheader(f"Match {i} – {st.session_state.matches[key]['format']}")
                # ... (your player selection and per-hole number_input code here)
                st.markdown('</div>', unsafe_allow_html=True)

# (Add your leaderboard / player points as before)

st.caption("If blank on iPhone: Try Chrome app, or refresh after 5–10 sec. Report what shows (title only? loading spinner?)")
