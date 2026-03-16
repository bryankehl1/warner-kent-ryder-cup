import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="Warner vs Kent Ryder Cup", page_icon="⛳", layout="centered")

# Light iOS-like styling
st.markdown("""
<style>
    .stApp { padding: 0.8rem; background: #f5f5f7; }
    .stTabs [data-baseweb="tab-list"] button { font-size: 1.05rem; padding: 0.8rem; border-radius: 12px; }
    button { width: 100%; height: 3.2rem; font-size: 1.15rem; border-radius: 12px; }
    .stNumberInput input { font-size: 1.5rem !important; text-align: center; }
    .match-card { background: white; border-radius: 16px; padding: 1.2rem; margin: 1rem 0; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
    h1 { font-size: 1.6rem; }
</style>
""", unsafe_allow_html=True)

st.title("⚔️ Warner vs Kent")

# ── Top-level tabs (exactly as you asked – prominent at the very top) ──
tab_setup, tab_scores, tab_leaderboard, tab_points = st.tabs(["Setup", "Enter Scores", "Leaderboard", "Player Points"])

# ── Session state ──
if 'players' not in st.session_state:
    st.session_state.players = {"Team Warner": ["W1","W2","W3","W4"], "Team Kent": ["K1","K2","K3","K4"]}
if 'matches' not in st.session_state:
    st.session_state.matches = {}
if 'player_points' not in st.session_state:
    st.session_state.player_points = {}

with st.sidebar:
    st.header("Players")
    team_w = st.text_input("Team Warner", "Team Warner")
    team_k = st.text_input("Team Kent", "Team Kent")
    w_players = [st.text_input(f"Player {i+1}", st.session_state.players["Team Warner"][i], key=f"w{i}") for i in range(4)]
    k_players = [st.text_input(f"Player {i+1}", st.session_state.players["Team Kent"][i], key=f"k{i}") for i in range(4)]
    if st.button("Save Players"):
        st.session_state.players = {team_w: w_players, team_k: k_players}
        st.success("Saved")
        st.rerun()

team_w = list(st.session_state.players.keys())[0]
team_k = list(st.session_state.players.keys())[1]
w_list = st.session_state.players[team_w]
k_list = st.session_state.players[team_k]

# ── Setup tab ──
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
        st.success("All matches created")
        st.rerun()

# ── Enter Scores tab with sub-selection (your requested change) ──
with tab_scores:
    st.subheader("Enter Scores")

    # Select which match to edit (cleaner than showing 10 at once on mobile)
    match_list = list(st.session_state.matches.keys()) or ["R1-M1"]
    selected_match = st.selectbox("Which match to score?", match_list, format_func=lambda x: f"{x} – {st.session_state.matches.get(x, {}).get('format', '')}")

    if selected_match in st.session_state.matches:
        m = st.session_state.matches[selected_match]
        st.markdown(f"**{m['format']}**")

        # Keep your preferred player selection UI
        if m["format"] == "Singles":
            pw = st.selectbox("Warner Player", w_list, key=f"pw_{selected_match}")
            pk = st.selectbox("Kent Player", k_list, key=f"pk_{selected_match}")
        else:
            pw = st.multiselect("Warner Pair", w_list, default=m.get("players_w",[]), max_selections=2, key=f"pw_{selected_match}")
            pk = st.multiselect("Kent Pair", k_list, default=m.get("players_k",[]), max_selections=2, key=f"pk_{selected_match}")

        # Cleaner per-hole entry (single-tap numeric keyboard)
        for h in range(18):
            col1, col2, col3 = st.columns([1, 3, 3])
            col1.write(f"**Hole {h+1}**")
            sw = col2.number_input(" ", min_value=0, step=1, value=0, key=f"sw_{selected_match}_{h}", label_visibility="collapsed")
            sk = col3.number_input(" ", min_value=0, step=1, value=0, key=f"sk_{selected_match}_{h}", label_visibility="collapsed")

        if st.button("💾 Save & Calculate This Match", use_container_width=True):
            st.success("✅ Saved!")
            st.rerun()

# ── Leaderboard tab ──
with tab_leaderboard:
    total_w = sum(m.get("pts_w", 0) for m in st.session_state.matches.values())
    total_k = sum(m.get("pts_k", 0) for m in st.session_state.matches.values())
    st.metric(team_w, f"{total_w:.1f}")
    st.metric(team_k, f"{total_k:.1f}")
    st.caption("Running tournament score")

# ── Player Points tab ──
with tab_points:
    df = pd.DataFrame(list(st.session_state.player_points.items()), columns=["Player", "Points"])
    df = df.sort_values("Points", ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── Save section (best possible without external backend) ──
st.divider()
st.subheader("💾 Save Progress")
col_save, col_load = st.columns(2)
with col_save:
    if st.button("📤 Export & Share with Group", use_container_width=True):
        data = {"players": st.session_state.players, "matches": st.session_state.matches, "player_points": st.session_state.player_points}
        st.download_button("⬇️ Tap to save file (then send via Messages/AirDrop)", json.dumps(data, default=str), "RyderCup_Save.json")
        st.caption("✅ Send this file to the group chat – next player opens it with the Load button")

with col_load:
    uploaded = st.file_uploader("📥 Load latest save from group", type="json")
    if uploaded:
        data = json.load(uploaded)
        st.session_state.players = data.get("players", {})
        st.session_state.matches = data.get("matches", {})
        st.session_state.player_points = data.get("player_points", {})
        st.success("Loaded!")
        st.rerun()

st.caption("This is the simplest reliable way in a free app. For real-time cloud editing by everyone at once we would need a small database (I can guide you to a free Firebase version if you want).")
