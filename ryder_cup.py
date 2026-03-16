import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="Warner vs Kent Ryder Cup", page_icon="⛳", layout="wide")

# ── Initialize session state ──
if 'players' not in st.session_state:
    st.session_state.players = {
        "Team Warner": ["Player W1", "Player W2", "Player W3", "Player W4"],
        "Team Kent": ["Player K1", "Player K2", "Player K3", "Player K4"]
    }

if 'matches' not in st.session_state:
    st.session_state.matches = {}

if 'player_points' not in st.session_state:
    st.session_state.player_points = {}

# Update player_points if players change
all_players = [p for ps in st.session_state.players.values() for p in ps]
for p in all_players:
    if p not in st.session_state.player_points:
        st.session_state.player_points[p] = 0.0

st.title("Warner vs Kent Ryder Cup Scorekeeper")

# ── Sidebar: Players ──
with st.sidebar:
    st.header("Teams & Players")

    team_a = st.text_input("Team A", "Team Warner", key="team_a_name")
    team_b = st.text_input("Team B", "Team Kent", key="team_b_name")

    st.subheader(f"{team_a} Players")
    players_a = [st.text_input(f"P{i+1}", st.session_state.players.get(team_a, [""]*4)[i], key=f"pa_{i}") for i in range(4)]

    st.subheader(f"{team_b} Players")
    players_b = [st.text_input(f"P{i+1}", st.session_state.players.get(team_b, [""]*4)[i], key=f"pb_{i}") for i in range(4)]

    if st.button("Save Teams & Players"):
        st.session_state.players = {team_a: players_a, team_b: players_b}
        st.success("Saved! Refreshing...")
        st.rerun()

    st.markdown("---")
    st.caption("**Debug Info**")
    st.caption(f"Players loaded: {len(st.session_state.players.get(team_a, []))} + {len(st.session_state.players.get(team_b, []))}")
    st.caption(f"Matches loaded: {len(st.session_state.matches)}")

# Current values after possible save
team_a = list(st.session_state.players.keys())[0]
team_b = list(st.session_state.players.keys())[1]
players_a = st.session_state.players[team_a]
players_b = st.session_state.players[team_b]

# ── Tabs ──
tab1, tab2, tab3, tab4 = st.tabs(["Setup", "Scores", "Leaderboard", "Player Points"])

with tab1:
    st.subheader("Match Setup")

    if st.button("Create All 10 Matches"):
        formats = [("R1", "Foursomes", 2), ("R2", "Fourball", 2), ("R3", "Greensomes", 2), ("R4", "Singles", 4)]
        for round_code, fmt, count in formats:
            for m in range(1, count + 1):
                key = f"{round_code}-M{m}"
                if key not in st.session_state.matches:
                    st.session_state.matches[key] = {
                        "round": round_code,
                        "format": fmt,
                        "players_a": players_a[:2] if fmt != "Singles" else [players_a[0]],
                        "players_b": players_b[:2] if fmt != "Singles" else [players_b[0]],
                        "holes": 18,
                        "scores_a": [0] * 18,
                        "scores_b": [0] * 18,
                        "ind_a": [0] * 18 if fmt == "Singles" else None,
                        "ind_b": [0] * 18 if fmt == "Singles" else None,
                        "points_a": 0.0,
                        "points_b": 0.0,
                        "completed": False
                    }
        st.success("All matches created!")
        st.rerun()

    st.caption(f"Matches now: {len(st.session_state.matches)}")

with tab2:
    st.subheader("Enter Scores")
    if not st.session_state.matches:
        st.warning("No matches exist yet. Create them in Setup tab.")
    else:
        round_choice = st.selectbox("Round", ["Round 1 – Foursomes", "Round 2 – Fourball", "Round 3 – Greensomes", "Round 4 – Singles"])
        r_prefix = round_choice[0:2]

        cols = st.columns(2 if "Singles" not in round_choice else 1)
        for idx, col in enumerate(cols if "Singles" not in round_choice else [st.container() for _ in range(4)]):
            with col:
                m_id = f"{r_prefix}-M{idx+1}"
                if m_id not in st.session_state.matches:
                    st.info(f"Match {idx+1} not created")
                    continue

                match = st.session_state.matches[m_id]
                st.subheader(f"Match {idx+1} – {match['format']}")

                # Player pick
                if match["format"] == "Singles":
                    pa = st.selectbox("Team A player", players_a, key=f"sa_{m_id}")
                    pb = st.selectbox("Team B player", players_b, key=f"sb_{m_id}")
                    match["players_a"] = [pa]
                    match["players_b"] = [pb]
                else:
                    pa = st.multiselect("Team A pair", players_a, default=match["players_a"], max_selections=2, key=f"ma_{m_id}")
                    pb = st.multiselect("Team B pair", players_b, default=match["players_b"], max_selections=2, key=f"mb_{m_id}")
                    match["players_a"] = pa
                    match["players_b"] = pb

                # Score entry
                if match["format"] == "Singles":
                    df = pd.DataFrame({
                        "Hole": range(1,19),
                        f"{pa}": match.get("ind_a", [0]*18),
                        f"{pb}": match.get("ind_b", [0]*18),
                        "Winner": [""]*18
                    })
                    ed = st.data_editor(df, width="stretch", hide_index=True, key=f"eds_{m_id}")
                    if st.button("Save Scores", key=f"btns_{m_id}"):
                        pa_pts = pb_pts = 0.0
                        for row in range(18):
                            sa = ed.iloc[row, 1]
                            sb = ed.iloc[row, 2]
                            if sa > 0 and sb > 0:
                                if sa < sb:
                                    pa_pts += 1
                                    ed.iloc[row, 3] = team_a
                                elif sb < sa:
                                    pb_pts += 1
                                    ed.iloc[row, 3] = team_b
                                else:
                                    pa_pts += 0.5
                                    pb_pts += 0.5
                                    ed.iloc[row, 3] = "½"
                        match["points_a"] = pa_pts
                        match["points_b"] = pb_pts
                        match["completed"] = True
                        st.session_state.player_points[pa] += pa_pts
                        st.session_state.player_points[pb] += pb_pts
                        st.success("Scores saved")
                else:
                    df = pd.DataFrame({
                        "Hole": range(1,19),
                        f"{team_a}": match["scores_a"],
                        f"{team_b}": match["scores_b"],
                        "Result": [""]*18
                    })
                    ed = st.data_editor(df, width="stretch", hide_index=True, key=f"edp_{m_id}")
                    if st.button("Save Scores", key=f"btnp_{m_id}"):
                        pa_pts = pb_pts = 0.0
                        for row in range(18):
                            sa = ed.iloc[row, 1]
                            sb = ed.iloc[row, 2]
                            if sa > 0 and sb > 0:
                                if sa < sb:
                                    pa_pts += 1
                                    ed.iloc[row, 3] = f"{team_a} wins"
                                elif sb < sa:
                                    pb_pts += 1
                                    ed.iloc[row, 3] = f"{team_b} wins"
                                else:
                                    pa_pts += 0.5
                                    pb_pts += 0.5
                                    ed.iloc[row, 3] = "Halved"
                        match["points_a"] = pa_pts
                        match["points_b"] = pb_pts
                        match["scores_a"] = ed["Team A"].tolist()
                        match["scores_b"] = ed["Team B"].tolist()
                        match["completed"] = True
                        for p in match["players_a"]: st.session_state.player_points[p] += pa_pts
                        for p in match["players_b"]: st.session_state.player_points[p] += pb_pts
                        st.success("Scores saved")

with tab3:
    total_a = sum(m["points_a"] for m in st.session_state.matches.values())
    total_b = sum(m["points_b"] for m in st.session_state.matches.values())
    col1, col2 = st.columns(2)
    col1.metric(team_a, f"{total_a:.1f}")
    col2.metric(team_b, f"{total_b:.1f}")

with tab4:
    df = pd.DataFrame(st.session_state.player_points.items(), columns=["Player", "Points"]).sort_values("Points", ascending=False)
    st.dataframe(df, width="stretch", hide_index=True)

# Export
if st.button("Export data"):
    data = {"players": st.session_state.players, "matches": st.session_state.matches, "points": st.session_state.player_points}
    st.download_button("Download JSON", json.dumps(data, default=str), "ryder_cup_data.json")
