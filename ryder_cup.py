import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="Warner vs Kent Ryder Cup", page_icon="⛳", layout="centered")

st.title("⚔️ Warner vs Kent Ryder Cup")

# Mobile-friendly sync (best compromise for phones on the course)
st.subheader("🔄 Save & Load Tournament")
col_exp, col_imp = st.columns(2)
with col_exp:
    if st.button("📤 Export & Save to Phone", use_container_width=True):
        data = {
            "players": st.session_state.get("players", {}),
            "matches": st.session_state.get("matches", {}),
            "player_points": st.session_state.get("player_points", {})
        }
        st.download_button(
            label="⬇️ Tap to save file to Files app",
            data=json.dumps(data, indent=2, default=str),
            file_name=f"RyderCup_{datetime.now().strftime('%H%M')}.json",
            mime="application/json"
        )
        st.caption("✅ Save to Files app → share via Messages/AirDrop to group")

with col_imp:
    uploaded = st.file_uploader("📥 Load from Files app", type="json")
    if uploaded:
        try:
            data = json.load(uploaded)
            st.session_state.players = data.get("players", {})
            st.session_state.matches = data.get("matches", {})
            st.session_state.player_points = data.get("player_points", {})
            st.success("✅ Loaded successfully!")
            st.rerun()
        except:
            st.error("File invalid – use the exported file")

# Players
with st.expander("👥 Edit Teams & Players"):
    team_w = st.text_input("Team Warner", "Team Warner")
    team_k = st.text_input("Team Kent", "Team Kent")
    w_players = [st.text_input(f"Player {i+1}", "Player W" + str(i+1), key=f"w{i}") for i in range(4)]
    k_players = [st.text_input(f"Player {i+1}", "Player K" + str(i+1), key=f"k{i}") for i in range(4)]
    if st.button("Save Players"):
        st.session_state.players = {team_w: w_players, team_k: k_players}
        st.success("Players saved")
        st.rerun()

team_w = list(st.session_state.players.keys())[0] if st.session_state.players else "Team Warner"
team_k = list(st.session_state.players.keys())[1] if len(st.session_state.players) > 1 else "Team Kent"
w_list = st.session_state.players.get(team_w, ["W1","W2","W3","W4"])
k_list = st.session_state.players.get(team_k, ["K1","K2","K3","K4"])

# Tabs – all restored
tab1, tab2, tab3, tab4 = st.tabs(["Setup", "Enter Scores", "Leaderboard", "Player Points"])

with tab1:
    st.subheader("Create Matches")
    if st.button("Create All 10 Matches", use_container_width=True):
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
        st.success("All matches created")
        st.rerun()

with tab2:
    st.subheader("Enter Scores")
    round_sel = st.selectbox("Round", ["Round 1 – Foursomes", "Round 2 – Fourball", "Round 3 – Greensomes", "Round 4 – Singles"])
    rkey = round_sel.split(" – ")[0].replace("Round ", "R")

    for i in range(1, 5 if "Singles" in round_sel else 3):
        key = f"{rkey}-M{i}"
        if key in st.session_state.matches:
            m = st.session_state.matches[key]
            st.subheader(f"Match {i} – {m['format']}")

            # Player selection
            if m["format"] == "Singles":
                pw = st.selectbox("Warner Player", w_list, key=f"pw{i}")
                pk = st.selectbox("Kent Player", k_list, key=f"pk{i}")
            else:
                pw = st.multiselect("Warner Pair", w_list, default=m.get("players_w",[]), key=f"pairw{i}")
                pk = st.multiselect("Kent Pair", k_list, default=m.get("players_k",[]), key=f"pairk{i}")

            # Per-hole numeric input (single tap numeric keyboard on iPhone)
            for h in range(18):
                colh, colw, colk = st.columns([1, 2, 2])
                colh.write(f"**Hole {h+1}**")
                sw = colw.number_input(" ", min_value=0, step=1, value=0, key=f"sw_{key}_{h}", label_visibility="collapsed")
                sk = colk.number_input(" ", min_value=0, step=1, value=0, key=f"sk_{key}_{h}", label_visibility="collapsed")

            if st.button(f"💾 Save Match {i}", use_container_width=True, key=f"save{i}"):
                st.success(f"Match {i} saved ✅")
                st.rerun()

with tab3:
    total_w = sum(m.get("pts_w", 0) for m in st.session_state.matches.values())
    total_k = sum(m.get("pts_k", 0) for m in st.session_state.matches.values())
    st.metric(team_w, f"{total_w:.1f} pts")
    st.metric(team_k, f"{total_k:.1f} pts")

with tab4:
    df = pd.DataFrame(list(st.session_state.player_points.items()), columns=["Player", "Points"])
    df = df.sort_values("Points", ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)

st.caption("💡 On the course: Export → save to Files → share via Messages. Next player opens and Imports. Refresh works with Load button.")
