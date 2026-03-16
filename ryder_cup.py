import streamlit as st
import pandas as pd
import json
from datetime import datetime

# ── Custom CSS for mobile-friendly, modern app look ──
st.markdown("""
<style>
    .stApp { max-width: 100%; padding: 1rem; background: #f8f9fa; }
    .block-container { padding-top: 1rem !important; padding-bottom: 6rem !important; }
    button {
        width: 100%;
        height: 3.2rem;
        font-size: 1.1rem;
        border-radius: 12px;
        background: #0066cc;
        color: white;
        border: none;
        margin: 0.6rem 0;
    }
    .stNumberInput > div > div > input {
        font-size: 1.5rem !important;
        height: 3.2rem !important;
        text-align: center;
        border-radius: 8px;
        border: 1px solid #ccc;
    }
    .match-card {
        background: white;
        border-radius: 16px;
        padding: 1.4rem;
        margin: 1.2rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
    }
    .match-header {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1a1a1a;
    }
    .hole-label {
        font-weight: bold;
        font-size: 1.1rem;
        text-align: center;
        margin: 0.4rem 0;
    }
    h1, h2, h3 { color: #1a1a1a; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Warner vs Kent Ryder Cup", page_icon="⛳", layout="wide")

# ── Session state init ──
if 'players' not in st.session_state:
    st.session_state.players = {
        "Team Warner": ["Player W1", "Player W2", "Player W3", "Player W4"],
        "Team Kent": ["Player K1", "Player K2", "Player K3", "Player K4"]
    }
if 'matches' not in st.session_state:
    st.session_state.matches = {}
if 'player_points' not in st.session_state:
    st.session_state.player_points = {}

st.title("Warner vs Kent Ryder Cup")

# ── Mobile-friendly sync ──
with st.expander("Sync / Backup (tap to open)", expanded=False):
    col_copy, col_paste = st.columns(2)
    with col_copy:
        if st.button("Generate JSON to Copy"):
            export = {
                "players": st.session_state.players,
                "matches": st.session_state.matches,
                "player_points": st.session_state.player_points
            }
            st.code(json.dumps(export, indent=2, default=str), language="json")
            st.caption("Long-press → Copy")
    with col_paste:
        paste = st.text_area("Paste JSON here to load", height=120)
        if st.button("Load from Pasted JSON") and paste.strip():
            try:
                data = json.loads(paste)
                st.session_state.players = data.get("players", st.session_state.players)
                st.session_state.matches = data.get("matches", {})
                st.session_state.player_points = data.get("player_points", {})
                st.success("Loaded!")
                st.rerun()
            except Exception as e:
                st.error(f"Error loading: {e}")

# ── Players setup ──
with st.expander("Edit Teams & Players", expanded=False):
    team_w = st.text_input("Team Warner Name", "Team Warner")
    team_k = st.text_input("Team Kent Name", "Team Kent")

    st.subheader(team_w)
    w_players = [st.text_input(f"Player {i+1}", st.session_state.players.get(team_w, [""]*4)[i], key=f"wp_{i}") for i in range(4)]

    st.subheader(team_k)
    k_players = [st.text_input(f"Player {i+1}", st.session_state.players.get(team_k, [""]*4)[i], key=f"kp_{i}") for i in range(4)]

    if st.button("Save Players"):
        st.session_state.players = {team_w: w_players, team_k: k_players}
        st.success("Saved")
        st.rerun()

team_w = list(st.session_state.players.keys())[0]
team_k = list(st.session_state.players.keys())[1]
w_list = st.session_state.players[team_w]
k_list = st.session_state.players[team_k]

# ── Tabs ──
tab_setup, tab_scores, tab_lb, tab_pp = st.tabs(["Setup", "Scores", "Leaderboard", "Player Points"])

with tab_setup:
    st.subheader("Create Matches")
    if st.button("Create All 10 Matches"):
        for r, fmt, count in [("R1", "Foursomes", 2), ("R2", "Fourball", 2), ("R3", "Greensomes", 2), ("R4", "Singles", 4)]:
            for m in range(1, count + 1):
                key = f"{r}-M{m}"
                if key not in st.session_state.matches:
                    st.session_state.matches[key] = {
                        "format": fmt,
                        "players_w": w_list[:2] if fmt != "Singles" else [w_list[0]],
                        "players_k": k_list[:2] if fmt != "Singles" else [k_list[0]],
                        "scores_w": [0]*18,
                        "scores_k": [0]*18,
                        "ind_w": [0]*18 if fmt == "Singles" else None,
                        "ind_k": [0]*18 if fmt == "Singles" else None,
                        "pts_w": 0.0,
                        "pts_k": 0.0
                    }
        st.success("Created!")
        st.rerun()

with tab_scores:
    round_sel = st.selectbox("Select Round", ["Round 1 – Foursomes", "Round 2 – Fourball", "Round 3 – Greensomes", "Round 4 – Singles"])
    r_map = {"Round 1":"R1", "Round 2":"R2", "Round 3":"R3", "Round 4":"R4"}
    r_key = r_map[round_sel.split(" – ")[0]]

    num_matches = 4 if "Singles" in round_sel else 2
    for i in range(1, num_matches + 1):
        m_key = f"{r_key}-M{i}"
        if m_key in st.session_state.matches:
            m = st.session_state.matches[m_key]
            with st.container():
                st.markdown('<div class="match-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="match-header">Match {i} – {m["format"]}</div>', unsafe_allow_html=True)

                # Players
                if m["format"] == "Singles":
                    pw = st.selectbox("Warner player", w_list, key=f"spw_{m_key}")
                    pk = st.selectbox("Kent player", k_list, key=f"spk_{m_key}")
                    m["players_w"] = [pw]
                    m["players_k"] = [pk]
                else:
                    pw = st.multiselect("Warner pair", w_list, default=m.get("players_w", []), max_selections=2, key=f"mpw_{m_key}")
                    pk = st.multiselect("Kent pair", k_list, default=m.get("players_k", []), max_selections=2, key=f"mpk_{m_key}")
                    m["players_w"] = pw
                    m["players_k"] = pk

                # Hole-by-hole numeric inputs (mobile-optimized)
                st.markdown('<div class="hole-label">Hole Scores</div>', unsafe_allow_html=True)
                cols = st.columns(3) if m["format"] == "Singles" else st.columns(2)
                scores_w = m.get("scores_w" if m["format"] != "Singles" else "ind_w", [0]*18)
                scores_k = m.get("scores_k" if m["format"] != "Singles" else "ind_k", [0]*18)

                for h in range(18):
                    with cols[h % len(cols)]:
                        st.markdown(f"**Hole {h+1}**")
                        sw = st.number_input(" ", min_value=0, step=1, value=int(scores_w[h]), key=f"sw_{m_key}_{h}", label_visibility="collapsed")
                        sk = st.number_input(" ", min_value=0, step=1, value=int(scores_k[h]), key=f"sk_{m_key}_{h}", label_visibility="collapsed")
                        scores_w[h] = sw
                        scores_k[h] = sk

                if st.button("Save & Calculate Match", key=f"save_{m_key}"):
                    if m["format"] == "Singles":
                        m["ind_w"] = scores_w
                        m["ind_k"] = scores_k
                    else:
                        m["scores_w"] = scores_w
                        m["scores_k"] = scores_k
                    # Add point calculation here if needed
                    st.success("Match saved!")
                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

with tab_lb:
    total_w = sum(m.get("pts_w", 0) for m in st.session_state.matches.values())
    total_k = sum(m.get("pts_k", 0) for m in st.session_state.matches.values())
    st.metric(team_w, f"{total_w:.1f}")
    st.metric(team_k, f"{total_k:.1f}")

with tab_pp:
    df = pd.DataFrame(st.session_state.player_points.items(), columns=["Player", "Points"]).sort_values("Points", ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)

st.caption("Tip: After changes, copy JSON from Sync section and share it in your group chat. Paste on next open to continue.")
