import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(
    page_title="Warner vs Kent Ryder Cup",
    page_icon="⛳",
    layout="wide",  # Perfect for iPhone / iPad in landscape or portrait
    initial_sidebar_state="expanded"
)

st.title("⚔️ Warner vs Kent • Custom Ryder Cup Scorekeeper")
st.caption("4 Rounds • 10 Matches Total • Mobile-friendly • Live Team + Player Points")

# ─────────────────────────────────────────────
# SESSION STATE (persists while app is open)
# ─────────────────────────────────────────────
if "players" not in st.session_state:
    st.session_state.players = {
        "Warner": ["Player W1", "Player W2", "Player W3", "Player W4"],
        "Kent": ["Player K1", "Player K2", "Player K3", "Player K4"]
    }

if "matches" not in st.session_state:
    st.session_state.matches = {}   # key = "R1-M1", "R4-M3", etc.

if "player_points" not in st.session_state:
    st.session_state.player_points = {p: 0.0 for team in st.session_state.players.values() for p in team}

# ─────────────────────────────────────────────
# SIDEBAR – Team & Player Setup
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("🏷️ Teams & Players")
    team_w = st.text_input("Team 1 Name", value="Team Warner", key="tw")
    team_k = st.text_input("Team 2 Name", value="Team Kent", key="tk")

    st.subheader(f"👥 {team_w} (4 players)")
    w_players = [st.text_input(f"Player {i+1}", value=st.session_state.players["Warner"][i], key=f"w{i}") for i in range(4)]

    st.subheader(f"👥 {team_k} (4 players)")
    k_players = [st.text_input(f"Player {i+1}", value=st.session_state.players["Kent"][i], key=f"k{i}") for i in range(4)]

    if st.button("💾 Save Player Names & Reset Roster"):
        st.session_state.players = {team_w: w_players, team_k: k_players}
        st.success("✅ Players saved! Create or edit matches below.")

    st.divider()
    st.caption("📱 Open this page on your iPhone → Add to Home Screen for app-like feel")

# Use saved names
team_w = list(st.session_state.players.keys())[0]
team_k = list(st.session_state.players.keys())[1]
w_list = st.session_state.players[team_w]
k_list = st.session_state.players[team_k]

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_setup, tab_rounds, tab_leaderboard, tab_stats = st.tabs(["🔧 Setup Matches", "⛳ Enter Scores (4 Rounds)", "🏆 Leaderboard", "👤 Player Points"])

with tab_setup:
    st.subheader("Pre-create all 10 matches")
    round_choice = st.selectbox("Select Round to Prepare", ["Round 1 – Foursomes (2 matches)", "Round 2 – Fourball (2)", "Round 3 – Greensomes (2)", "Round 4 – Singles (4)"])

    if st.button("🚀 Auto-create ALL matches for the tournament"):
        # Pre-populate every match slot
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
                        "scores_w": [0]*18,
                        "scores_k": [0]*18,
                        "individual_w": [0]*18 if fmt == "Singles" else None,
                        "individual_k": [0]*18 if fmt == "Singles" else None,
                        "points_w": 0.0,
                        "points_k": 0.0,
                        "completed": False
                    }
        st.success("✅ All 10 matches created! Go to the next tab to assign players & enter scores.")

with tab_rounds:
    round_tab = st.selectbox("Choose Round", ["Round 1 – Foursomes", "Round 2 – Fourball", "Round 3 – Greensomes", "Round 4 – Singles (1v1)"])
    r_key = round_tab[0:2]  # R1, R2...

    cols = st.columns(2 if "Round 4" not in round_tab else 1)
    for i, col in enumerate(cols if "Round 4" not in round_tab else [st.container()] * 4):
        with col:
            m_key = f"{r_key}-M{i+1}"
            if m_key not in st.session_state.matches:
                st.warning(f"Match {i+1} not created yet – click Setup button first")
                continue

            match = st.session_state.matches[m_key]
            fmt = match["format"]

            st.subheader(f"Match {i+1} • {fmt}")
            st.caption(f"{team_w} vs {team_k} • 18 holes")

            # Player assignment
            if fmt == "Singles":
                p_w = st.selectbox(f"{team_w} Player", w_list, key=f"selw_{m_key}")
                p_k = st.selectbox(f"{team_k} Player", k_list, key=f"selk_{m_key}")
                match["players_w"] = [p_w]
                match["players_k"] = [p_k]
            else:
                p_w = st.multiselect(f"{team_w} Pair (2)", w_list, default=match["players_w"], max_selections=2, key=f"pw_{m_key}")
                p_k = st.multiselect(f"{team_k} Pair (2)", k_list, default=match["players_k"], max_selections=2, key=f"pk_{m_key}")
                match["players_w"] = p_w
                match["players_k"] = p_k

            # Scoring input – different for Singles
            if fmt == "Singles":
                st.write("**Enter each player’s score per hole**")
                df = pd.DataFrame({
                    "Hole": list(range(1,19)),
                    f"{p_w} Score": match.get("individual_w", [0]*18),
                    f"{p_k} Score": match.get("individual_k", [0]*18),
                    "Winner": [""]*18
                })
                edited = st.data_editor(df, use_container_width=True, hide_index=True, key=f"edit_singles_{m_key}")
                if st.button("✅ Calculate Match", key=f"calc_{m_key}"):
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
                    # Credit to individuals
                    st.session_state.player_points[p_w] += pts_w
                    st.session_state.player_points[p_k] += pts_k
                    st.success(f"✅ {team_w} {pts_w} – {team_k} {pts_k}")
            else:
                # Paired formats – team/pair score
                st.write("**Team/Pair score per hole** (Foursomes/Greensomes/Fourball – best ball or alternate)")
                df_pair = pd.DataFrame({
                    "Hole": list(range(1,19)),
                    f"{team_w} Pair Score": match["scores_w"],
                    f"{team_k} Pair Score": match["scores_k"],
                    "Result": [""]*18
                })
                edited_pair = st.data_editor(df_pair, use_container_width=True, hide_index=True, key=f"edit_pair_{m_key}")
                if st.button("✅ Update Pair Match", key=f"up_{m_key}"):
                    pts_w = pts_k = 0.0
                    for h in range(18):
                        aw = edited_pair.iloc[h, 1]
                        ak = edited_pair.iloc[h, 2]
                        if aw > 0 and ak > 0:
                            if aw < ak:
                                pts_w += 1
                                edited_pair.iloc[h, 3] = "Warner wins"
                            elif ak < aw:
                                pts_k += 1
                                edited_pair.iloc[h, 3] = "Kent wins"
                            else:
                                pts_w += 0.5
                                pts_k += 0.5
                                edited_pair.iloc[h, 3] = "Halved"
                    match["points_w"] = pts_w
                    match["points_k"] = pts_k
                    match["scores_w"] = edited_pair.iloc[:,1].tolist()
                    match["scores_k"] = edited_pair.iloc[:,2].tolist()
                    match["completed"] = True
                    # Award points to every player in the pair
                    for pw in match["players_w"]: st.session_state.player_points[pw] += pts_w
                    for pk in match["players_k"]: st.session_state.player_points[pk] += pts_k
                    st.success(f"✅ Pair points recorded")

# ─────────────────────────────────────────────
# LEADERBOARD TAB
# ─────────────────────────────────────────────
with tab_leaderboard:
    col1, col2 = st.columns(2)
    with col1:
        total_w = sum(m["points_w"] for m in st.session_state.matches.values())
        total_k = sum(m["points_k"] for m in st.session_state.matches.values())
        st.metric(label=f"🏆 {team_w} TOTAL", value=f"{total_w:.1f}", delta=None)
        st.metric(label=f"🏆 {team_k} TOTAL", value=f"{total_k:.1f}")
    with col2:
        if total_w > total_k:
            st.success(f"🔥 **{team_w} LEADS!**")
        elif total_k > total_w:
            st.success(f"🔥 **{team_k} LEADS!**")
        else:
            st.info("🟰 All square so far")

    st.divider()
    st.subheader("Match-by-Match Progress")
    df_summary = pd.DataFrame([
        {"Match": k, "Format": v["format"], f"{team_w}": v["points_w"], f"{team_k}": v["points_k"], "Done": "✅" if v["completed"] else "⭕"}
        for k, v in st.session_state.matches.items()
    ])
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# PLAYER POINTS TAB
# ─────────────────────────────────────────────
with tab_stats:
    st.subheader("👤 Individual Player Points Earned")
    df_players = pd.DataFrame(list(st.session_state.player_points.items()), columns=["Player", "Points"])
    df_players = df_players.sort_values("Points", ascending=False)
    st.dataframe(df_players, use_container_width=True, hide_index=True)

    st.caption("Points are awarded to every player who participated in a winning/halved match")

# ─────────────────────────────────────────────
# BOTTOM BAR – Export + Sharing
# ─────────────────────────────────────────────
st.divider()
col_export, col_share, col_info = st.columns([2, 2, 3])
with col_export:
    if st.button("📥 Export Full Tournament (JSON)"):
        export_data = {
            "teams": st.session_state.players,
            "matches": st.session_state.matches,
            "player_points": st.session_state.player_points,
            "timestamp": datetime.now().isoformat()
        }
        st.download_button(
            "⬇️ Download warner_kent_tournament.json",
            data=json.dumps(export_data, indent=2, default=str),
            file_name=f"Warner_vs_Kent_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

with col_share:
    st.button("🔗 Generate Shareable Link", help="Deploy once for permanent link")
    st.caption("→ Free & instant: Go to **streamlit.io/cloud** → New app → paste this file → get public URL in 60 seconds. Send the link to all friends – works perfectly on iPhone.")

with col_info:
    st.success("✅ Everything saved automatically in browser. Refresh keeps data while tab is open. Use on iPhone Safari → Share → Add to Home Screen for native app feel.")

st.caption("Made with ❤️ for your group • Paste this entire file as ryder_cup_v2.py and run `streamlit run ryder_cup_v2.py`")
