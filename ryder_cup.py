import streamlit as st
import pandas as pd
import pyrebase

# ─────────────────────────────────────────────
# FIREBASE CONFIG
# ─────────────────────────────────────────────
firebaseConfig = {
    "apiKey": "AIzaSyBHxFmZYsVSm4clbXpE4u-1LFZSW8Mg5CE",
    "authDomain": "warner-kent-ryder-cup.firebaseapp.com",
    "databaseURL": "https://warner-kent-ryder-cup-default-rtdb.firebaseio.com",
    "projectId": "warner-kent-ryder-cup",
    "storageBucket": "warner-kent-ryder-cup.firebasestorage.app",
    "messagingSenderId": "364132704196",
    "appId": "1:364132704196:web:4348ae83bb93eb1ecf8e91"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# ─────────────────────────────────────────────
# PAGE CONFIG & CSS
# ─────────────────────────────────────────────
st.set_page_config(page_title="Warner vs Kent Ryder Cup", page_icon="⛳", layout="centered")

st.markdown("""
<style>
    /* Base app */
    .stApp { padding: 0.8rem; background: #f0f4f0; }

    /* Fix button text color on ALL platforms including iOS Safari */
    .stButton > button {
        width: 100%;
        min-height: 3.2rem;
        font-size: 1.05rem;
        border-radius: 12px;
        font-weight: 600;
        color: #ffffff !important;
        background-color: #2e7d32 !important;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1b5e20 !important;
        color: #ffffff !important;
    }
    .stButton > button:active {
        background-color: #1b5e20 !important;
        color: #ffffff !important;
    }

    /* Number inputs */
    .stNumberInput input {
        font-size: 1.4rem !important;
        text-align: center;
    }

    /* Match cards */
    .match-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }

    /* Score row highlights */
    .hole-w { color: #1565C0; font-weight: bold; }
    .hole-k { color: #b71c1c; font-weight: bold; }
    .hole-h { color: #555; }

    /* Leaderboard team banners */
    .team-banner-w {
        background: #1565C0;
        color: white;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .team-banner-k {
        background: #b71c1c;
        color: white;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .vs-text {
        text-align: center;
        font-size: 1.2rem;
        color: #555;
        margin: 0.3rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("⛳ Warner vs Kent Ryder Cup")

# ─────────────────────────────────────────────
# SESSION STATE INITIALISATION
# ─────────────────────────────────────────────
def init_state():
    if "players" not in st.session_state:
        st.session_state.players = {}
    if "matches" not in st.session_state:
        st.session_state.matches = {}
    if "player_points" not in st.session_state:
        st.session_state.player_points = {}
    if "firebase_loaded" not in st.session_state:
        st.session_state.firebase_loaded = False

init_state()

# ─────────────────────────────────────────────
# FIREBASE LOAD  (once per session, or on demand)
# ─────────────────────────────────────────────
def load_from_firebase():
    try:
        data = db.get().val() or {}
        st.session_state.players       = data.get("players", st.session_state.players)
        st.session_state.matches       = data.get("matches", st.session_state.matches)
        st.session_state.player_points = data.get("player_points", st.session_state.player_points)
        st.session_state.firebase_loaded = True
    except Exception as e:
        st.warning(f"⚠️ Firebase load failed: {e}. Using local state.")

if not st.session_state.firebase_loaded:
    load_from_firebase()

# ─────────────────────────────────────────────
# HELPER: derive team names / player lists safely
# ─────────────────────────────────────────────
def get_teams():
    pd_ = st.session_state.players
    keys = list(pd_.keys())
    tw = keys[0] if len(keys) > 0 else "Team Warner"
    tk = keys[1] if len(keys) > 1 else "Team Kent"
    wl = pd_.get(tw, ["W1","W2","W3","W4"])
    kl = pd_.get(tk, ["K1","K2","K3","K4"])
    return tw, tk, wl, kl

# ─────────────────────────────────────────────
# MATCH-PLAY POINT CALCULATOR
# ─────────────────────────────────────────────
def calculate_match_play(scores_w, scores_k, fmt):
    """
    Returns (pts_w, pts_k, hole_results, status_str)
    hole_results: list of 'W', 'K', or 'H' for each hole played
    Greensomes: lower of the two balls per side after drives,
                treated identically to Foursomes for scoring here
                (one score per side per hole).
    Singles / Fourball: same hole-by-hole comparison.
    """
    hole_results = []
    w_up = 0          # positive = Warner leading, negative = Kent leading
    holes_played = 0
    match_over_at = None

    for h in range(18):
        sw = scores_w[h]
        sk = scores_k[h]

        # Skip unplayed holes (both 0)
        if sw == 0 and sk == 0:
            hole_results.append(None)
            continue

        holes_played += 1
        holes_remaining = 18 - h  # includes this hole

        if sw < sk:
            hole_results.append("W")
            w_up += 1
        elif sk < sw:
            hole_results.append("K")
            w_up -= 1
        else:
            hole_results.append("H")

        # Check if match is mathematically over (dormie / won)
        holes_left = 18 - (h + 1)
        if abs(w_up) > holes_left and match_over_at is None:
            match_over_at = h + 1

    # Determine result
    if holes_played == 0:
        return 0.0, 0.0, hole_results, "Not started"

    if w_up > 0:
        margin = w_up
        holes_left = 18 - holes_played
        if match_over_at:
            status = f"Warner wins {margin}&{holes_left}"
        else:
            status = f"Warner {margin} UP"
        pts_w, pts_k = 1.0, 0.0
    elif w_up < 0:
        margin = abs(w_up)
        holes_left = 18 - holes_played
        if match_over_at:
            status = f"Kent wins {margin}&{holes_left}"
        else:
            status = f"Kent {margin} UP"
        pts_w, pts_k = 0.0, 1.0
    else:
        status = "All Square"
        pts_w, pts_k = 0.5, 0.5

    # Only award full points if all 18 holes recorded OR match decided
    if holes_played < 18 and match_over_at is None:
        pts_w = 0.0
        pts_k = 0.0
        status += " (in progress)"

    return pts_w, pts_k, hole_results, status

# ─────────────────────────────────────────────
# RECALCULATE ALL PLAYER POINTS
# ─────────────────────────────────────────────
def recalculate_player_points():
    pp = {}
    for key, m in st.session_state.matches.items():
        pts_w = m.get("pts_w", 0.0)
        pts_k = m.get("pts_k", 0.0)
        for p in m.get("players_w", []):
            pp[p] = pp.get(p, 0.0) + pts_w
        for p in m.get("players_k", []):
            pp[p] = pp.get(p, 0.0) + pts_k
    st.session_state.player_points = pp
    db.child("player_points").set(pp)

# ─────────────────────────────────────────────
# SIDEBAR – TEAM SETUP
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("🏌️ Teams & Players")
    tw_input = st.text_input("Team Warner name", "Team Warner")
    tk_input = st.text_input("Team Kent name", "Team Kent")

    st.markdown("**Warner Players**")
    tw_tmp, tk_tmp, wl_tmp, kl_tmp = get_teams()
    w_inputs = [
        st.text_input(f"W{i+1}", wl_tmp[i] if i < len(wl_tmp) else "", key=f"wp_{i}")
        for i in range(4)
    ]
    st.markdown("**Kent Players**")
    k_inputs = [
        st.text_input(f"K{i+1}", kl_tmp[i] if i < len(kl_tmp) else "", key=f"kp_{i}")
        for i in range(4)
    ]

    if st.button("💾 Save Players"):
        st.session_state.players = {tw_input: w_inputs, tk_input: k_inputs}
        db.child("players").set(st.session_state.players)
        st.success("Players saved & synced!")
        st.rerun()

    if st.button("🔄 Refresh from Firebase"):
        st.session_state.firebase_loaded = False
        st.rerun()

# Re-derive after possible sidebar save
team_w, team_k, w_list, k_list = get_teams()

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_setup, tab_scores, tab_lb, tab_pp = st.tabs(["⚙️ Setup", "🏌️ Scores", "🏆 Leaderboard", "👤 Player Points"])

# ══════════════════════════════════════════════
# TAB 1 – SETUP
# ══════════════════════════════════════════════
with tab_setup:
    st.subheader("Tournament Format")
    st.markdown("""
    | Round | Format | Matches |
    |-------|--------|---------|
    | R1 | Foursomes (Alternate Shot) | 2 |
    | R2 | Fourball (Best Ball) | 2 |
    | R3 | Greensomes | 2 |
    | R4 | Singles Match Play | 4 |
    """)
    st.markdown("**Total: 10 matches · 10 points available**")

    st.divider()

    # Build the match schedule with proper player assignment
    schedule = [
        # (key, format, w_players, k_players)
        ("R1-M1", "Foursomes", [w_list[0], w_list[1]], [k_list[0], k_list[1]]),
        ("R1-M2", "Foursomes", [w_list[2], w_list[3]], [k_list[2], k_list[3]]),
        ("R2-M1", "Fourball",  [w_list[0], w_list[1]], [k_list[0], k_list[1]]),
        ("R2-M2", "Fourball",  [w_list[2], w_list[3]], [k_list[2], k_list[3]]),
        ("R3-M1", "Greensomes",[w_list[0], w_list[1]], [k_list[0], k_list[1]]),
        ("R3-M2", "Greensomes",[w_list[2], w_list[3]], [k_list[2], k_list[3]]),
        ("R4-M1", "Singles",   [w_list[0]],            [k_list[0]]),
        ("R4-M2", "Singles",   [w_list[1]],            [k_list[1]]),
        ("R4-M3", "Singles",   [w_list[2]],            [k_list[2]]),
        ("R4-M4", "Singles",   [w_list[3]],            [k_list[3]]),
    ]

    st.markdown("**Proposed Pairings:**")
    for key, fmt, pw, pk in schedule:
        st.markdown(f"- **{key}** ({fmt}): {' & '.join(pw)} vs {' & '.join(pk)}")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Create All 10 Matches", use_container_width=True):
            new_matches = {}
            for key, fmt, pw, pk in schedule:
                existing = st.session_state.matches.get(key, {})
                new_matches[key] = {
                    "format": fmt,
                    "players_w": pw,
                    "players_k": pk,
                    "scores_w": existing.get("scores_w", [0]*18),
                    "scores_k": existing.get("scores_k", [0]*18),
                    "pts_w": existing.get("pts_w", 0.0),
                    "pts_k": existing.get("pts_k", 0.0),
                }
            st.session_state.matches = new_matches
            db.child("matches").set(new_matches)
            st.success("✅ All 10 matches created & synced!")
            st.rerun()

    with col2:
        if st.button("🗑️ Reset All Scores", use_container_width=True):
            for key in st.session_state.matches:
                st.session_state.matches[key]["scores_w"] = [0]*18
                st.session_state.matches[key]["scores_k"] = [0]*18
                st.session_state.matches[key]["pts_w"] = 0.0
                st.session_state.matches[key]["pts_k"] = 0.0
            db.child("matches").set(st.session_state.matches)
            st.session_state.player_points = {}
            db.child("player_points").set({})
            st.success("Scores reset!")
            st.rerun()

# ══════════════════════════════════════════════
# TAB 2 – ENTER SCORES
# ══════════════════════════════════════════════
with tab_scores:
    st.subheader("Enter Scores")
    match_keys = list(st.session_state.matches.keys())

    if not match_keys:
        st.info("No matches yet – go to ⚙️ Setup and create matches first.")
    else:
        # Format the dropdown nicely
        def fmt_key(k):
            m = st.session_state.matches[k]
            pw = " & ".join(m.get("players_w", []))
            pk = " & ".join(m.get("players_k", []))
            return f"{k} ({m['format']}) · {pw} vs {pk}"

        selected_key = st.selectbox("Select Match", match_keys, format_func=fmt_key)
        m = st.session_state.matches[selected_key]
        fmt = m["format"]

        # Show match info
        st.markdown(f"""
        <div class='match-card'>
        <b>{selected_key}</b> · {fmt}<br>
        🔵 {team_w}: <b>{' & '.join(m.get('players_w', []))}</b><br>
        🔴 {team_k}: <b>{' & '.join(m.get('players_k', []))}</b>
        </div>
        """, unsafe_allow_html=True)

        # Player reassignment (optional, for flexibility)
        with st.expander("✏️ Edit Players for this Match"):
            if fmt == "Singles":
                new_pw = st.selectbox("Warner Player", w_list,
                    index=w_list.index(m["players_w"][0]) if m["players_w"] and m["players_w"][0] in w_list else 0,
                    key=f"pw_{selected_key}")
                new_pk = st.selectbox("Kent Player", k_list,
                    index=k_list.index(m["players_k"][0]) if m["players_k"] and m["players_k"][0] in k_list else 0,
                    key=f"pk_{selected_key}")
                if st.button("Update Players", key=f"upd_{selected_key}"):
                    st.session_state.matches[selected_key]["players_w"] = [new_pw]
                    st.session_state.matches[selected_key]["players_k"] = [new_pk]
                    db.child("matches").child(selected_key).update({"players_w": [new_pw], "players_k": [new_pk]})
                    st.success("Players updated!")
                    st.rerun()
            else:
                new_pw = st.multiselect("Warner Pair", w_list,
                    default=[p for p in m.get("players_w", []) if p in w_list],
                    max_selections=2, key=f"mpw_{selected_key}")
                new_pk = st.multiselect("Kent Pair", k_list,
                    default=[p for p in m.get("players_k", []) if p in k_list],
                    max_selections=2, key=f"mpk_{selected_key}")
                if st.button("Update Players", key=f"upd_{selected_key}"):
                    st.session_state.matches[selected_key]["players_w"] = new_pw
                    st.session_state.matches[selected_key]["players_k"] = new_pk
                    db.child("matches").child(selected_key).update({"players_w": new_pw, "players_k": new_pk})
                    st.success("Players updated!")
                    st.rerun()

        st.divider()

        # ── Hole-by-hole score entry ──
        st.markdown(f"**Enter scores hole by hole** (0 = not played)")
        saved_w = m.get("scores_w", [0]*18)
        saved_k = m.get("scores_k", [0]*18)

        # Ensure lists are exactly 18 long
        if not isinstance(saved_w, list): saved_w = [0]*18
        if not isinstance(saved_k, list): saved_k = [0]*18
        while len(saved_w) < 18: saved_w.append(0)
        while len(saved_k) < 18: saved_k.append(0)

        col_h, col_w, col_k = st.columns([1, 3, 3])
        col_h.markdown("**Hole**")
        col_w.markdown(f"**🔵 {team_w}**")
        col_k.markdown(f"**🔴 {team_k}**")

        new_scores_w = []
        new_scores_k = []

        for h in range(18):
            col_h, col_w, col_k = st.columns([1, 3, 3])
            col_h.markdown(f"**{h+1}**")
            sw = col_w.number_input(
                "w", min_value=0, max_value=20, step=1,
                value=int(saved_w[h]) if saved_w[h] else 0,
                key=f"sw_{selected_key}_{h}",
                label_visibility="collapsed"
            )
            sk = col_k.number_input(
                "k", min_value=0, max_value=20, step=1,
                value=int(saved_k[h]) if saved_k[h] else 0,
                key=f"sk_{selected_key}_{h}",
                label_visibility="collapsed"
            )
            new_scores_w.append(sw)
            new_scores_k.append(sk)

        st.divider()

        # ── Live preview ──
        pts_w_prev, pts_k_prev, hole_results, status_prev = calculate_match_play(
            new_scores_w, new_scores_k, fmt
        )

        # Show running status
        played_holes = [r for r in hole_results if r is not None]
        if played_holes:
            st.markdown(f"**Live Status:** {status_prev}")
            # Mini scorecard
            result_row = []
            for r in hole_results:
                if r == "W":    result_row.append(f"🔵")
                elif r == "K":  result_row.append(f"🔴")
                elif r == "H":  result_row.append(f"⚪")
                else:           result_row.append("·")
            # Show in 2 rows of 9
            cols = st.columns(9)
            for i, (c, sym) in enumerate(zip(cols, result_row[:9])):
                c.markdown(f"<div style='text-align:center;font-size:1.1rem'>{sym}<br><small>{i+1}</small></div>", unsafe_allow_html=True)
            cols2 = st.columns(9)
            for i, (c, sym) in enumerate(zip(cols2, result_row[9:18])):
                c.markdown(f"<div style='text-align:center;font-size:1.1rem'>{sym}<br><small>{i+10}</small></div>", unsafe_allow_html=True)

        st.divider()

        if st.button("💾 Save & Calculate Match", use_container_width=True, key=f"save_{selected_key}"):
            pts_w, pts_k, _, status = calculate_match_play(new_scores_w, new_scores_k, fmt)
            st.session_state.matches[selected_key]["scores_w"] = new_scores_w
            st.session_state.matches[selected_key]["scores_k"] = new_scores_k
            st.session_state.matches[selected_key]["pts_w"] = pts_w
            st.session_state.matches[selected_key]["pts_k"] = pts_k
            db.child("matches").child(selected_key).update({
                "scores_w": new_scores_w,
                "scores_k": new_scores_k,
                "pts_w": pts_w,
                "pts_k": pts_k
            })
            recalculate_player_points()
            st.success(f"✅ Saved! Result: {status} · {team_w} {pts_w:.1f}pt – {team_k} {pts_k:.1f}pt")
            st.rerun()

# ══════════════════════════════════════════════
# TAB 3 – LEADERBOARD
# ══════════════════════════════════════════════
with tab_lb:
    st.subheader("🏆 Team Leaderboard")

    total_w = sum(float(m.get("pts_w", 0)) for m in st.session_state.matches.values())
    total_k = sum(float(m.get("pts_k", 0)) for m in st.session_state.matches.values())
    total_available = 10.0

    # Team banners
    col_w, col_vs, col_k = st.columns([5, 2, 5])
    with col_w:
        st.markdown(f"""
        <div class='team-banner-w'>
            {team_w}<br>{total_w:.1f}
        </div>""", unsafe_allow_html=True)
    with col_vs:
        st.markdown("<div class='vs-text' style='padding-top:1.5rem'>vs</div>", unsafe_allow_html=True)
    with col_k:
        st.markdown(f"""
        <div class='team-banner-k'>
            {team_k}<br>{total_k:.1f}
        </div>""", unsafe_allow_html=True)

    # Points needed to win
    needed = total_available / 2 + 0.5
    st.markdown(f"**{needed:.1f} points needed to win · {total_available - total_w - total_k:.1f} points still to play**")

    if total_w >= needed:
        st.success(f"🏆 {team_w} WIN THE RYDER CUP!")
    elif total_k >= needed:
        st.success(f"🏆 {team_k} WIN THE RYDER CUP!")
    elif total_w == total_k == total_available / 2:
        st.info("🤝 It's a TIE — Cup retained by the holders!")

    st.divider()

    # Match-by-match breakdown
    st.markdown("**Match Results**")
    round_labels = {"R1": "Round 1 – Foursomes", "R2": "Round 2 – Fourball",
                    "R3": "Round 3 – Greensomes", "R4": "Round 4 – Singles"}
    current_round = None

    for key in sorted(st.session_state.matches.keys()):
        m = st.session_state.matches[key]
        rnd = key.split("-")[0]
        if rnd != current_round:
            current_round = rnd
            st.markdown(f"##### {round_labels.get(rnd, rnd)}")

        pts_w = float(m.get("pts_w", 0))
        pts_k = float(m.get("pts_k", 0))
        pw_str = " & ".join(m.get("players_w", []))
        pk_str = " & ".join(m.get("players_k", []))

        if pts_w > pts_k:
            result_icon = "🔵"
        elif pts_k > pts_w:
            result_icon = "🔴"
        elif pts_w == 0.5:
            result_icon = "⚪"
        else:
            result_icon = "⏳"

        _, _, _, status = calculate_match_play(
            m.get("scores_w", [0]*18),
            m.get("scores_k", [0]*18),
            m.get("format", "")
        )

        st.markdown(f"{result_icon} **{key}**: {pw_str} vs {pk_str} · *{status}* · **{pts_w:.1f} – {pts_k:.1f}**")

# ══════════════════════════════════════════════
# TAB 4 – PLAYER POINTS
# ══════════════════════════════════════════════
with tab_pp:
    st.subheader("👤 Individual Player Points")

    pp = st.session_state.player_points
    if not pp:
        st.info("No player points yet – save some match scores first.")
    else:
        rows = []
        for player, pts in pp.items():
            # Determine team
            if player in w_list:
                team_label = team_w
                color = "🔵"
            elif player in k_list:
                team_label = team_k
                color = "🔴"
            else:
                team_label = "Unknown"
                color = "⚪"
            rows.append({"": color, "Player": player, "Team": team_label, "Points": float(pts)})

        df = pd.DataFrame(rows).sort_values("Points", ascending=False).reset_index(drop=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Highlight top scorer
        if not df.empty:
            top = df.iloc[0]
            st.markdown(f"🥇 **Top scorer: {top['Player']} ({top['Points']:.1f} pts)**")

st.divider()
st.caption("⛳ Live sync via Firebase · Refresh anytime to pull latest scores · Built for Warner vs Kent Ryder Cup")
