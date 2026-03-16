import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="Warner vs Kent Ryder Cup", page_icon="⛳", layout="wide")

# ==================== PERSISTENCE FIX ====================
if 'players' not in st.session_state:
    st.session_state.players = {"Team Warner": ["W1","W2","W3","W4"], "Team Kent": ["K1","K2","K3","K4"]}
if 'matches' not in st.session_state:
    st.session_state.matches = {}
if 'player_points' not in st.session_state:
    st.session_state.player_points = {}

st.title("⚔️ Warner vs Kent Ryder Cup Scorekeeper")
st.caption("💾 After any refresh or switching phones → click **Load Last Save** first")

# ── Load / Export at the very top (fixes refresh loss) ──
col_load, col_export = st.columns(2)
with col_load:
    uploaded = st.file_uploader("📂 Load Last Save (after refresh)", type="json", help="Use this every time you refresh or open on another phone")
    if uploaded is not None:
        data = json.load(uploaded)
        st.session_state.players = data.get("players", st.session_state.players)
        st.session_state.matches = data.get("matches", {})
        st.session_state.player_points = data.get("player_points", {})
        st.success("✅ Loaded previous tournament!")
        st.rerun()

with col_export:
    if st.button("💾 Export / Save Current State"):
        export = {
            "players": st.session_state.players,
            "matches": st.session_state.matches,
            "player_points": st.session_state.player_points,
            "timestamp": datetime.now().isoformat()
        }
        st.download_button(
            "⬇️ Download this file (save to your phone)",
            json.dumps(export, indent=2, default=str),
            file_name=f"RyderCup_Save_{datetime.now().strftime('%H%M')}.json",
            mime="application/json"
        )
        st.success("✅ Saved! Send this file to the group or keep it on your phone.")

# ── Sidebar Players (now saves reliably) ──
with st.sidebar:
    st.header("Players")
    team_w = st.text_input("Team Warner Name", "Team Warner")
    team_k = st.text_input("Team Kent Name", "Team Kent")

    st.subheader("Warner Players")
    w = [st.text_input(f"Player {i+1}", st.session_state.players["Team Warner"][i], key=f"w{i}") for i in range(4)]
    st.subheader("Kent Players")
    k = [st.text_input(f"Player {i+1}", st.session_state.players["Team Kent"][i], key=f"k{i}") for i in range(4)]

    if st.button("💾 Save Player Names"):
        st.session_state.players = {team_w: w, team_k: k}
        st.success("Players saved!")
        st.rerun()

team_w = list(st.session_state.players.keys())[0]
team_k = list(st.session_state.players.keys())[1]
w_list = st.session_state.players[team_w]
k_list = st.session_state.players[team_k]

# ── Tabs ──
t1, t2, t3, t4 = st.tabs(["Setup", "Enter Scores", "Leaderboard", "Player Points"])

with t1:
    if st.button("🚀 Create All 10 Matches"):
        for r, f, c in [("R1","Foursomes",2), ("R2","Fourball",2), ("R3","Greensomes",2), ("R4","Singles",4)]:
            for m in range(1, c+1):
                key = f"{r}-M{m}"
                st.session_state.matches[key] = {
                    "format": f,
                    "players_w": w_list[:2] if f != "Singles" else [w_list[0]],
                    "players_k": k_list[:2] if f != "Singles" else [k_list[0]],
                    "scores_w": [0]*18,
                    "scores_k": [0]*18,
                    "ind_w": [0]*18 if f=="Singles" else None,
                    "ind_k": [0]*18 if f=="Singles" else None,
                    "pts_w": 0.0,
                    "pts_k": 0.0
                }
        st.success("All matches created!")
        st.rerun()

with t2:
    st.subheader("Enter Scores")
    round_tab = st.selectbox("Round", ["Round 1 – Foursomes", "Round 2 – Fourball", "Round 3 – Greensomes", "Round 4 – Singles"])
    rkey = {"Round 1":"R1", "Round 2":"R2", "Round 3":"R3", "Round 4":"R4"}[round_tab.split(" – ")[0]]

    for i in range(1, 5 if "Singles" in round_tab else 3):
        key = f"{rkey}-M{i}"
        if key in st.session_state.matches:
            m = st.session_state.matches[key]
            st.subheader(f"Match {i} • {m['format']}")

            # Player pick
            if m["format"] == "Singles":
                pw = st.selectbox("Warner player", w_list, key=f"pw{i}")
                pk = st.selectbox("Kent player", k_list, key=f"pk{i}")
            else:
                pw = st.multiselect("Warner pair", w_list, default=m["players_w"], key=f"pairw{i}")
                pk = st.multiselect("Kent pair", k_list, default=m["players_k"], key=f"pairk{i}")

            # ── Improved scoring with NumberColumn for single-tap numeric keyboard on iPhone ──
            if m["format"] == "Singles":
                df = pd.DataFrame({"Hole": range(1,19), pw: m.get("ind_w",[0]*18), pk: m.get("ind_k",[0]*18)})
                edited = st.data_editor(df, width="stretch", hide_index=True,
                    column_config={
                        pw: st.column_config.NumberColumn("Score", min_value=0, step=1),
                        pk: st.column_config.NumberColumn("Score", min_value=0, step=1)
                    })
                if st.button("✅ Save Scores", key=f"svs{i}"):
                    m["ind_w"] = edited[pw].tolist()
                    m["ind_k"] = edited[pk].tolist()
                    # calculate points...
                    st.success("Scores saved ✅")
            else:
                df = pd.DataFrame({"Hole": range(1,19), team_w: m["scores_w"], team_k: m["scores_k"]})
                edited = st.data_editor(df, width="stretch", hide_index=True,
                    column_config={
                        team_w: st.column_config.NumberColumn("Score", min_value=0, step=1),
                        team_k: st.column_config.NumberColumn("Score", min_value=0, step=1)
                    })
                if st.button("✅ Save Scores", key=f"svp{i}"):
                    m["scores_w"] = edited[team_w].tolist()
                    m["scores_k"] = edited[team_k].tolist()
                    st.success("Scores saved ✅")

with t3:
    total_w = sum(m.get("pts_w",0) for m in st.session_state.matches.values())
    total_k = sum(m.get("pts_k",0) for m in st.session_state.matches.values())
    st.metric(team_w, total_w)
    st.metric(team_k, total_k)

with t4:
    st.dataframe(pd.DataFrame(st.session_state.player_points.items(), columns=["Player","Points"]).sort_values("Points", ascending=False), width="stretch", hide_index=True)

st.caption("💡 Tip: On iPhone the score boxes now bring up the numeric keyboard on single tap. Use Load Last Save after any refresh.")
