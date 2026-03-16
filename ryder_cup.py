import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="Warner vs Kent Ryder Cup", page_icon="⛳", layout="wide")

# ── Init session state ──
if 'players' not in st.session_state:
    st.session_state.players = {
        "Team Warner": ["Player W1", "Player W2", "Player W3", "Player W4"],
        "Team Kent": ["Player K1", "Player K2", "Player K3", "Player K4"]
    }

if 'matches' not in st.session_state:
    st.session_state.matches = {}

if 'player_points' not in st.session_state:
    st.session_state.player_points = {}

st.title("⚔️ Warner vs Kent Ryder Cup Scorekeeper")

# ── Mobile-friendly JSON sync (copy-paste instead of file upload) ──
st.subheader("Sync / Restore Tournament (Mobile-Friendly)")
col1, col2 = st.columns(2)

with col1:
    st.caption("Copy this to share / backup")
    if st.button("Generate JSON to Copy"):
        export = {
            "players": st.session_state.players,
            "matches": {k: v for k, v in st.session_state.matches.items()},
            "player_points": st.session_state.player_points
        }
        json_str = json.dumps(export, indent=2, default=str)
        st.code(json_str, language="json")
        st.caption("Long-press → Copy")

with col2:
    st.caption("Paste JSON from another phone to restore")
    paste_json = st.text_area("Paste JSON here", height=150, key="paste_json")
    if st.button("Load Pasted JSON") and paste_json.strip():
        try:
            data = json.loads(paste_json)
            st.session_state.players = data.get("players", st.session_state.players)
            st.session_state.matches = data.get("matches", {})
            st.session_state.player_points = data.get("player_points", {})
            st.success("Restored from pasted JSON!")
            st.rerun()
        except Exception as e:
            st.error(f"Invalid JSON: {e}")

# ── Players Sidebar ──
with st.sidebar:
    st.header("Players")
    team_w = st.text_input("Team A", "Team Warner", key="team_w")
    team_k = st.text_input("Team B", "Team Kent", key="team_k")

    st.subheader(team_w)
    w_players = [st.text_input(f"P{i+1}", value=st.session_state.players.get(team_w, [""]*4)[i], key=f"wp_{i}") for i in range(4)]

    st.subheader(team_k)
    k_players = [st.text_input(f"P{i+1}", value=st.session_state.players.get(team_k, [""]*4)[i], key=f"kp_{i}") for i in range(4)]

    if st.button("Save Players"):
        st.session_state.players = {team_w: w_players, team_k: k_players}
        st.success("Players saved")
        st.rerun()

team_w = list(st.session_state.players.keys())[0]
team_k = list(st.session_state.players.keys())[1]
w_list = st.session_state.players[team_w]
k_list = st.session_state.players[team_k]

# ── Tabs ──
tab_setup, tab_scores, tab_lb, tab_pp = st.tabs(["Setup", "Scores", "Leaderboard", "Player Points"])

with tab_setup:
    if st.button("Create All 10 Matches"):
        for r, fmt, cnt in [("R1","Foursomes",2), ("R2","Fourball",2), ("R3","Greensomes",2), ("R4","Singles",4)]:
            for m in range(1, cnt+1):
                key = f"{r}-M{m}"
                if key not in st.session_state.matches:
                    st.session_state.matches[key] = {
                        "format": fmt,
                        "players_w": w_list[:2] if fmt != "Singles" else [w_list[0]],
                        "players_k": k_list[:2] if fmt != "Singles" else [k_list[0]],
                        "scores_w": [0]*18,
                        "scores_k": [0]*18,
                        "ind_w": [0]*18 if fmt=="Singles" else None,
                        "ind_k": [0]*18 if fmt=="Singles" else None,
                        "pts_w": 0.0,
                        "pts_k": 0.0,
                        "completed": False
                    }
        st.success("Matches created")
        st.rerun()

with tab_scores:
    round_sel = st.selectbox("Round", ["Round 1 – Foursomes", "Round 2 – Fourball", "Round 3 – Greensomes", "Round 4 – Singles (1v1)"])
    r_map = {"Round 1":"R1", "Round 2":"R2", "Round 3":"R3", "Round 4":"R4"}
    r_key = r_map[round_sel.split(" – ")[0]]

    count = 4 if "Singles" in round_sel else 2
    cols = st.columns(2 if count == 2 else 1)
    for idx, col in enumerate(cols if count == 2 else [st.container() for _ in range(4)]):
        with col:
            m_key = f"{r_key}-M{idx+1}"
            if m_key not in st.session_state.matches:
                st.info(f"Match {idx+1} not created")
                continue

            m = st.session_state.matches[m_key]
            st.subheader(f"Match {idx+1} – {m['format']}")

            # Players
            if m["format"] == "Singles":
                pw = st.selectbox("Warner", w_list, key=f"spw_{m_key}")
                pk = st.selectbox("Kent", k_list, key=f"spk_{m_key}")
                m["players_w"] = [pw]
                m["players_k"] = [pk]
            else:
                pw = st.multiselect("Warner pair", w_list, default=m.get("players_w", []), max_selections=2, key=f"mpw_{m_key}")
                pk = st.multiselect("Kent pair", k_list, default=m.get("players_k", []), max_selections=2, key=f"mpk_{m_key}")
                m["players_w"] = pw
                m["players_k"] = pk

            # Scoring with persistence + numeric keyboard
            if m["format"] == "Singles":
                df = pd.DataFrame({
                    "Hole": range(1,19),
                    pw: m.get("ind_w", [0]*18),
                    pk: m.get("ind_k", [0]*18),
                    "Winner": [""]*18
                })
                ed = st.data_editor(
                    df,
                    width="stretch",
                    hide_index=True,
                    key=f"edit_s_{m_key}_{m['format']}",  # unique per match/format
                    column_config={
                        pw: st.column_config.NumberColumn("Score", min_value=0, step=1),
                        pk: st.column_config.NumberColumn("Score", min_value=0, step=1)
                    }
                )
                if st.button("Save & Calc", key=f"save_s_{m_key}"):
                    m["ind_w"] = ed[pw].tolist()
                    m["ind_k"] = ed[pk].tolist()
                    # Add point calc here if needed
                    st.success("Saved")
                    st.rerun()
            else:
                df = pd.DataFrame({
                    "Hole": range(1,19),
                    team_w: m.get("scores_w", [0]*18),
                    team_k: m.get("scores_k", [0]*18),
                    "Result": [""]*18
                })
                ed = st.data_editor(
                    df,
                    width="stretch",
                    hide_index=True,
                    key=f"edit_p_{m_key}_{m['format']}",  # unique
                    column_config={
                        team_w: st.column_config.NumberColumn("Score", min_value=0, step=1),
                        team_k: st.column_config.NumberColumn("Score", min_value=0, step=1)
                    }
                )
                if st.button("Save & Calc", key=f"save_p_{m_key}"):
                    m["scores_w"] = ed[team_w].tolist()
                    m["scores_k"] = ed[team_k].tolist()
                    # Add point calc here if needed
                    st.success("Saved")
                    st.rerun()

# Leaderboard & Player Points tabs (add your existing code here if needed)

st.caption("After refresh → paste JSON or re-enter players. Scores now persist per match.")
