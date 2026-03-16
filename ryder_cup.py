import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(
    page_title="Warner vs Kent Ryder Cup",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Safe initial session state
if 'players' not in st.session_state:
    st.session_state.players = {
        "Team Warner": ["Player W1", "Player W2", "Player W3", "Player W4"],
        "Team Kent": ["Player K1", "Player K2", "Player K3", "Player K4"]
    }

if 'matches' not in st.session_state:
    st.session_state.matches = {}

if 'player_points' not in st.session_state:
    all_players = [p for team_players in st.session_state.players.values() for p in team_players]
    st.session_state.player_points = {p: 0.0 for p in all_players}

st.title("⚔️ Warner vs Kent • Custom Ryder Cup Scorekeeper")
st.caption("4 Rounds • 10 Matches • Mobile-friendly • Live Team & Player Points")

# ─────────────────────────────────────────────
# SIDEBAR – Teams & Players
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("Teams & Players")
    
    current_teams = list(st.session_state.players.keys())
    team_w_name = current_teams[0] if current_teams else "Team Warner"
    team_k_name = current_teams[1] if len(current_teams) > 1 else "Team Kent"

    team_w = st.text_input("Team 1 Name", value=team_w_name)
    team_k = st.text_input("Team 2 Name", value=team_k_name)

    st.subheader(f"{team_w} Players")
    w_players = []
    for i in range(4):
        default = st.session_state.players.get(team_w, ["Player W1"]*4)[i]
        name = st.text_input(f"Player {i+1}", value=default, key=f"w_player_{i}")
        w_players.append(name)

    st.subheader(f"{team_k} Players")
    k_players = []
    for i in range(4):
        default = st.session_state.players.get(team_k, ["Player K1"]*4)[i]
        name = st.text_input(f"Player {i+1}", value=default, key=f"k_player_{i}")
        k_players.append(name)

    if st.button("💾 Save Teams & Players"):
        st.session_state.players = {team_w: w_players, team_k: k_players}
        all_players = w_players + k_players
        st.session_state.player_points = {p: st.session_state.player_points.get(p, 0.0) for p in all_players}
        st.success("Players saved!")
        st.rerun()

    st.divider()
    st.caption("Add to Home Screen on iPhone")

team_w = list(st.session_state.players.keys())[0]
team_k = list(st.session_state.players.keys())[1]
w_list = st.session_state.players[team_w]
k_list = st.session_state.players[team_k]

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_setup, tab_rounds, tab_leaderboard, tab_stats = st.tabs(
    ["Setup Matches", "Enter Scores", "Leaderboard", "Player Points"]
)

with tab_setup:
    st.subheader("Create Matches")

    if st.button("🚀 Auto-create all 10 matches"):
        for r, fmt, count in [("R1", "Foursomes", 2), ("R2", "Fourball", 2), ("R3", "Greensomes", 2), ("R4", "Singles", 4)]:
            for m in range(1, count + 1):
                key = f"{r}-M{m}"
                if key not in st.session_state.matches:
                    st.session_state.matches[key] = {
                        "round": r,
                        "format": fmt,
                        "players_w": w_list[:2] if fmt != "Singles" else [w_list[0]],
                        "players_k": k_list[:2] if fmt != "Singles" else [k_list[0]],
                        "holes": 18,
                        "scores_w": [0] * 18,
                        "scores_k": [0] * 18,
                        "individual_w": [0] * 18 if fmt == "Singles" else None,
                        "individual_k": [0] * 18 if fmt == "Singles" else None,
                        "points_w": 0.0,
                        "points_k": 0.0,
                        "completed": False
                    }
        st.success(f"Created {len(st.session_state.matches)} matches")
        st.rerun()

    st.subheader("Create one match manually")
    col_r, col_n = st.columns([3, 1])
    with col_r:
        round_choice = st.selectbox("Round", ["R1 - Foursomes", "R2 - Fourball", "R3 - Greensomes", "R4 - Singles"])
    with col_n:
        match_num = st.number_input("Match #", 1, 4, 1)

    if st.button("➕ Create this match"):
        r = round_choice[:2]
        fmt = round_choice.split(" - ")[1]
        key = f"{r}-M{match_num}"
        if key not in st.session_state.matches:
            st.session_state.matches[key] = {
                "round": r,
                "format": fmt,
                "players_w": w_list[:2] if fmt != "Singles" else [w_list[0]],
                "players_k": k_list[:2] if fmt != "Singles" else [k_list[0]],
                "holes": 18,
                "scores_w": [0] * 18,
                "scores_k": [0] * 18,
                "individual_w": [0] * 18 if fmt == "Singles" else None,
                "individual_k": [0] * 18 if fmt == "Singles" else None,
                "points_w": 0.0,
                "points_k": 0.0,
                "completed": False
            }
            st.success(f"Created {key}")
            st.rerun()
        else:
            st.info(f"{key} already exists")

    st.caption(f"Current matches loaded: **{len(st.session_state.matches)}**")

with tab_rounds:
    if not st.session_state.matches:
        st.warning("No matches yet. Go to Setup Matches tab and create some.")
    else:
        round_tab = st.selectbox("Round", ["Round 1 – Foursomes", "Round 2 – Fourball", "Round 3 – Greensomes", "Round 4 – Singles (1v1)"])
        r_key = round_tab[:2]

        cols = st.columns(2 if "Round 4" not in round_tab else 1)
        for i, col in enumerate(cols if "Round 4" not in round_tab else [st.container()] * 4):
            with col:
                m_key = f"{r_key}-M{i+1}"
                if m_key not in st.session_state.matches:
                    st.info(f"Match {i+1} not created yet")
                    continue

                match = st.session_state.matches[m_key]
                fmt = match["format"]

                st.subheader(f"Match {i+1} • {fmt}")

                # Player selection
                if fmt == "Singles":
                    p_w = st.selectbox(f"{team_w} player", w_list, key=f"sel_w_{m_key}")
                    p_k = st.selectbox(f"{team_k} player", k_list, key=f"sel_k_{m_key}")
                    match["players_w"] = [p_w]
                    match["players_k"] = [p_k]
                else:
                    p_w = st.multiselect(f"{team_w} pair", w_list, default=match.get("players_w", []), max_selections=2, key=f"pair_w_{m_key}")
                    p_k = st.multiselect(f"{team_k} pair", k_list, default=match.get("players_k", []), max_selections=2, key=f"pair_k_{m_key}")
                    match["players_w"] = p_w
                    match["players_k"] = p_k

                # Scoring
                if fmt == "Singles":
                    df = pd.DataFrame({
                        "Hole": range(1, 19),
                        f"{p_w}": match.get("individual_w", [0]*18),
                        f"{p_k}": match.get("individual_k", [0]*18),
                        "Winner": [""]*18
                    })
                    edited = st.data_editor(df, width="stretch", hide_index=True, key=f"edit_s_{m_key}")
                    if st.button("Save & Calculate", key=f"save_s_{m_key}"):
                        pts_w = pts_k = 0.0
                        for h in range(18):
                            sw = edited.iloc[h, 1]
                            sk = edited.iloc[h, 2]
                            if sw > 0 and sk > 0:
                                if sw < sk:
                                    pts_w += 1
                                    edited.iloc[h, 3] = team_w
                                elif sk < sw:
                                    pts_k += 1
                                    edited.iloc[h, 3] = team_k
                                else:
                                    pts_w += 0.5
                                    pts_k += 0.5
                                    edited.iloc[h, 3] = "½"
                        match["points_w"] = pts_w
                        match["points_k"] = pts_k
                        match["completed"] = True
                        st.session_state.player_points[p_w] += pts_w
                        st.session_state.player_points[p_k] += pts_k
                        st.success(f"{team_w} {pts_w} – {team_k} {pts_k}")
                else:
                    df = pd.DataFrame({
                        "Hole": range(1, 19),
                        f"{team_w}": match["scores_w"],
                        f"{team_k}": match["scores_k"],
                        "Result": [""]*18
                    })
                    edited = st.data_editor(df, width="stretch", hide_index=True, key=f"edit_p_{m_key}")
                    if st.button("Save & Calculate", key=f"save_p_{m_key}"):
                        pts_w = pts_k = 0.0
                        for h in range(18):
                            aw = edited.iloc[h, 1]
                            ak = edited.iloc[h, 2]
                            if aw > 0 and ak > 0:
                                if aw < ak:
                                    pts_w += 1
                                    edited.iloc[h, 3] = f"{team_w} wins"
                                elif ak < aw:
                                    pts_k += 1
                                    edited.iloc[h, 3] = f"{team_k} wins"
                                else:
                                    pts_w += 0.5
                                    pts_k += 0.5
                                    edited.iloc[h, 3] = "Halved"
                        match["points_w"] = pts_w
                        match["points_k"] = pts_k
                        match["scores_w"] = edited.iloc[:,1].tolist()
                        match["scores_k"] = edited.iloc[:,2].tolist()
                        match["completed"] = True
                        for p in match["players_w"]: st.session_state.player_points[p] += pts_w
                        for p in match["players_k"]: st.session_state.player_points[p] += pts_k
                        st.success(f"Points saved")

with tab_leaderboard:
    total_w = sum(m["points_w"] for m in st.session_state.matches.values())
    total_k = sum(m["points_k"] for m in st.session_state.matches.values())
    col1, col2 = st.columns(2)
    with col1:
        st.metric(team_w, f"{total_w:.1f}")
        st.metric(team_k, f"{total_k:.1f}")
    with col2:
        if total_w > total_k: st.success(f"{team_w} leads!")
        elif total_k > total_w: st.success(f"{team_k} leads!")
        else: st.info("Tied")

with tab_stats:
    df_p = pd.DataFrame(list(st.session_state.player_points.items()), columns=["Player", "Points"])
    df_p = df_p.sort_values("Points", ascending=False)
    st.dataframe(df_p, width="stretch", hide_index=True)

# Export
st.divider()
if st.button("Export JSON"):
    data = {
        "teams": st.session_state.players,
        "matches": st.session_state.matches,
        "player_points": st.session_state.player_points
    }
    st.download_button("Download", json.dumps(data, indent=2, default=str), "ryder_cup.json")
