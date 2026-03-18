import streamlit as st
import pandas as pd
import pyrebase

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

st.set_page_config(
    page_title="2026 Ryder Cup",
    page_icon="⛳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<meta name="color-scheme" content="light only">
<style>
    :root { color-scheme: light only !important; }
    *, *::before, *::after { color-scheme: light only !important; }
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"],
    [data-testid="stMain"],
    [data-testid="block-container"],
    [data-testid="stVerticalBlock"],
    [data-testid="stHeader"] {
        background-color: #f5f7f5 !important;
        color: #1a1a1a !important;
    }
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    @media (prefers-color-scheme: dark) {
        :root { color-scheme: light only !important; }
        html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stApp"],
        [data-testid="stMain"],
        [data-testid="block-container"],
        [data-testid="stVerticalBlock"],
        [data-testid="stHeader"] {
            background-color: #f5f7f5 !important;
            color: #1a1a1a !important;
        }
        [data-testid="stSidebar"],
        [data-testid="stSidebarContent"] {
            background-color: #ffffff !important;
            color: #1a1a1a !important;
        }
        p, h1, h2, h3, h4, h5, h6, span, label, div, a {
            color: #1a1a1a !important;
        }
        .stNumberInput input, .stTextInput input, textarea, select {
            background-color: #ffffff !important;
            color: #1a1a1a !important;
            border-color: #cccccc !important;
        }
        .stSelectbox > div > div,
        [data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #1a1a1a !important;
        }
        [data-baseweb="tab-list"],
        [data-baseweb="tab"] {
            background-color: #f5f7f5 !important;
            color: #1a1a1a !important;
        }
    }

    .stApp { padding: 0.5rem; }

    .stButton > button {
        width: 100%; min-height: 2.8rem; font-size: 1rem;
        border-radius: 10px; font-weight: 600;
        color: #ffffff !important;
        background-color: #2e7d32 !important;
        border: none;
    }
    .stButton > button:hover  { background-color: #1b5e20 !important; }
    .stButton > button:active { background-color: #1b5e20 !important; }

    .stNumberInput input {
        font-size: 1.1rem !important;
        text-align: center !important;
        padding: 0.2rem !important;
        height: 1.9rem !important;
    }
    .stNumberInput [data-testid="stNumberInputStepDown"],
    .stNumberInput [data-testid="stNumberInputStepUp"] {
        height: 1.9rem !important;
    }

    .score-label-w {
        font-size: 0.78rem; font-weight: 700; color: #FF6B7A;
        background: #fff0f3; border-radius: 20px;
        padding: 0.1rem 0.5rem; display: inline-block; margin-bottom: 0.1rem;
    }
    .score-label-k {
        font-size: 0.78rem; font-weight: 700; color: #1a7a6e;
        background: #eef7f5; border-radius: 20px;
        padding: 0.1rem 0.5rem; display: inline-block; margin-bottom: 0.1rem;
    }

    .match-card {
        background: white; border-radius: 12px;
        padding: 0.7rem 1rem; margin: 0.3rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        font-size: 0.92rem; line-height: 1.5;
    }

    .live-bar {
        position: sticky; top: 0; z-index: 999;
        background: #ffffff;
        border-left: 4px solid #2e7d32;
        border-radius: 0 10px 10px 0;
        padding: 0.45rem 0.8rem; margin-bottom: 0.6rem;
        box-shadow: 0 3px 10px rgba(0,0,0,0.12);
        font-size: 0.88rem;
    }

    .score-hdr-w {
        background: #fff0f3; border: 2px solid #FF6B7A;
        border-radius: 8px; padding: 0.3rem 0.5rem;
        font-size: 0.78rem; font-weight: 700; color: #FF6B7A; text-align: center;
    }
    .score-hdr-k {
        background: #f0f8f6; border: 2px solid #1a7a6e;
        border-radius: 8px; padding: 0.3rem 0.5rem;
        font-size: 0.78rem; font-weight: 700; color: #1a7a6e; text-align: center;
    }

    .warner { color: #FF6B7A !important; font-weight: 700; }
    .kent   { color: #1a7a6e !important; font-weight: 700; }
    .vs-text { text-align:center; font-size:1.1rem; color:#555; padding-top:1.2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='font-size:1.8rem;margin-bottom:0.2rem'>⛳ 2026 Ryder Cup</h1>",
            unsafe_allow_html=True)

# ── SESSION STATE ──
def init_state():
    for k, v in [("players",{}),("matches",{}),("player_points",{}),
                 ("firebase_loaded",False),
                 ("warner_name","Team Warner"),("kent_name","Team Kent")]:
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# ── FIREBASE ──
def load_from_firebase():
    try:
        data = db.get().val() or {}
        st.session_state.players       = data.get("players",       st.session_state.players)
        st.session_state.matches       = data.get("matches",       st.session_state.matches)
        st.session_state.player_points = data.get("player_points", st.session_state.player_points)
        st.session_state.warner_name   = data.get("warner_name",   st.session_state.warner_name)
        st.session_state.kent_name     = data.get("kent_name",     st.session_state.kent_name)
        st.session_state.firebase_loaded = True
    except Exception as e:
        st.warning(f"⚠️ Firebase load failed: {e}. Using local state.")

if not st.session_state.firebase_loaded:
    load_from_firebase()

for _k in list(st.session_state.players.keys()):
    if "warner" in _k.lower():
        st.session_state.warner_name = _k
    elif "kent" in _k.lower():
        st.session_state.kent_name = _k

# ── HELPERS ──
MSORT = lambda k: (int(k.split('-')[0][1:]) if k.split('-')[0][1:].isdigit() else 99,
                   int(k.split('-M')[1])     if '-M' in k and k.split('-M')[1].isdigit() else 99)

def get_teams():
    pd_ = st.session_state.players
    keys = list(pd_.keys())
    tw, tk = None, None
    for k in keys:
        if "warner" in k.lower(): tw = k
        elif "kent" in k.lower(): tk = k
    if tw is None: tw = st.session_state.get("warner_name", keys[0] if keys else "Team Warner")
    if tk is None: tk = st.session_state.get("kent_name",   keys[1] if len(keys)>1 else "Team Kent")
    wl = pd_.get(tw, ["W1","W2","W3","W4"])
    kl = pd_.get(tk, ["K1","K2","K3","K4"])
    return tw, tk, wl, kl

def calculate_match_play(scores_w, scores_k, fmt):
    hole_results, w_up, holes_played, match_over_at = [], 0, 0, None
    for h in range(18):
        sw, sk = scores_w[h], scores_k[h]
        if sw == 0 and sk == 0: hole_results.append(None); continue
        holes_played += 1
        if sw < sk:   hole_results.append("W"); w_up += 1
        elif sk < sw: hole_results.append("K"); w_up -= 1
        else:         hole_results.append("H")
        if abs(w_up) > 18-(h+1) and match_over_at is None: match_over_at = h+1
    if holes_played == 0: return 0.0, 0.0, hole_results, "Not started"
    hl = 18 - holes_played
    if w_up > 0:
        status = f"Warner wins {w_up}&{hl}" if match_over_at else f"Warner {w_up} UP"
        pts_w, pts_k = 1.0, 0.0
    elif w_up < 0:
        mg = abs(w_up)
        status = f"Kent wins {mg}&{hl}" if match_over_at else f"Kent {mg} UP"
        pts_w, pts_k = 0.0, 1.0
    else:
        status, pts_w, pts_k = "All Square", 0.5, 0.5
    if holes_played < 18 and match_over_at is None:
        pts_w = pts_k = 0.0; status += " (in progress)"
    return pts_w, pts_k, hole_results, status

def recalculate_player_points():
    pp = {}
    for m in st.session_state.matches.values():
        for p in m.get("players_w",[]): pp[p] = pp.get(p,0.0) + m.get("pts_w",0.0)
        for p in m.get("players_k",[]): pp[p] = pp.get(p,0.0) + m.get("pts_k",0.0)
    st.session_state.player_points = pp
    db.child("player_points").set(pp)

def hole_symbols(hole_results):
    out = []
    for r in hole_results:
        if r == "W":   out.append("<span style='color:#FF6B7A'>🌺</span>")
        elif r == "K": out.append("<span style='color:#1a7a6e'>🌿</span>")
        elif r == "H": out.append("<span style='color:#888'>·</span>")
        else:          out.append("<span style='color:#ccc'>·</span>")
    return "".join(out)

def score_tally(scores):
    """Sum of non-zero scores entered so far."""
    return sum(s for s in scores if s and s > 0)

def match_status_label(scores_w, scores_k):
    """Return compact match status: AS, 1 UP, 2 DN etc. from Warner perspective."""
    w_up = 0
    holes_played = 0
    for sw, sk in zip(scores_w, scores_k):
        if sw == 0 and sk == 0:
            continue
        holes_played += 1
        if sw < sk:   w_up += 1
        elif sk < sw: w_up -= 1
    if holes_played == 0:
        return ""
    if w_up == 0:
        return "AS"
    elif w_up > 0:
        return f"{w_up} UP"
    else:
        return f"{abs(w_up)} DN"

# ── COURSE PAR DATA ──
COURSE_PARS = {
    "R1": [5,3,4,5,4,4,3,4,4,4,4,4,3,4,4,5,3,5],  # Bloomington
    "R2": [4,4,3,4,4,4,5,3,5,4,4,4,5,4,3,4,3,5],  # Black Desert
    "R3": [5,3,4,5,4,4,3,4,4,4,4,4,3,4,4,5,3,5],  # Bloomington
}

def to_par_str(scores, round_key):
    """Return +N / E / -N string for strokes vs par through holes played."""
    pars = COURSE_PARS.get(round_key)
    if not pars:
        return ""
    total_strokes = sum(s for i,s in enumerate(scores) if s and s > 0 and i < len(pars))
    total_par     = sum(pars[i] for i,s in enumerate(scores) if s and s > 0 and i < len(pars))
    if total_strokes == 0:
        return "E"
    diff = total_strokes - total_par
    if diff == 0:  return "E"
    elif diff > 0: return f"+{diff}"
    else:          return f"{diff}"

def do_save(selected_key, new_scores_w, new_scores_k, fmt):
    pts_w, pts_k, _, status = calculate_match_play(new_scores_w, new_scores_k, fmt)
    st.session_state.matches[selected_key].update({
        "scores_w": new_scores_w, "scores_k": new_scores_k,
        "pts_w": pts_w, "pts_k": pts_k
    })
    db.child("matches").child(selected_key).update({
        "scores_w": new_scores_w, "scores_k": new_scores_k,
        "pts_w": pts_w, "pts_k": pts_k
    })
    recalculate_player_points()
    return pts_w, pts_k, status

# ── SIDEBAR ──
with st.sidebar:
    st.header("⛳ 2026 Ryder Cup")
    st.markdown("Use the **👥 Players** tab to set names & pairings.")
    st.divider()
    if st.button("🔄 Refresh from Firebase"):
        st.session_state.firebase_loaded = False
        st.rerun()
    st.caption("All changes sync live via Firebase.")

team_w, team_k, w_list, k_list = get_teams()

# ── PINNED LIVE LEADERBOARD ──
def render_pinned_leaderboard():
    total_w = sum(float(m.get("pts_w",0)) for m in st.session_state.matches.values())
    total_k = sum(float(m.get("pts_k",0)) for m in st.session_state.matches.values())
    total_available = 8.0   # 3 rounds, 8 matches
    needed = total_available / 2 + 0.5
    col_w, col_vs, col_k = st.columns([5,2,5])
    with col_w:
        st.markdown(f"""
        <div style='background:#FF6B7A;color:white;border-radius:12px;
                    padding:0.6rem 0.5rem;text-align:center;
                    font-size:1.15rem;font-weight:bold;'>
            🌺 {team_w}<br>{total_w:.1f}
        </div>""", unsafe_allow_html=True)
    with col_vs:
        st.markdown("<div class='vs-text' style='padding-top:0.9rem;font-size:0.95rem'>vs</div>",
                    unsafe_allow_html=True)
    with col_k:
        st.markdown(f"""
        <div style='background:#1a7a6e;color:white;border-radius:12px;
                    padding:0.6rem 0.5rem;text-align:center;
                    font-size:1.15rem;font-weight:bold;'>
            🌿 {team_k}<br>{total_k:.1f}
        </div>""", unsafe_allow_html=True)
    win_msg = ""
    if total_w >= needed:   win_msg = f" &nbsp;🏆 <b style='color:#2e7d32'>{team_w} WIN!</b>"
    elif total_k >= needed: win_msg = f" &nbsp;🏆 <b style='color:#2e7d32'>{team_k} WIN!</b>"
    elif total_w == total_k == total_available/2: win_msg = " &nbsp;🤝 <b>TIE!</b>"
    st.markdown(
        f"<div style='font-size:0.78rem;color:#555;margin:0.2rem 0 0.5rem 0'>"
        f"<b>{needed:.1f}</b> pts to win · <b>{total_available-total_w-total_k:.1f}</b> pts still to play"
        f"{win_msg}</div>", unsafe_allow_html=True)
    st.divider()

render_pinned_leaderboard()

# ── TABS ──
tab_setup, tab_players, tab_scores, tab_pp = st.tabs(
    ["⚙️ Format","👥 Players","🏌️ Scores","🏆 Points"])

# ══════════════════════════════════════════════
# TAB 1 – FORMAT
# ══════════════════════════════════════════════
with tab_setup:
    st.subheader("Tournament Format")
    st.markdown("""
| Round | Format | Matches |
|-------|--------|---------|
| R1 | Fourball (Best Ball) | 2 |
| R2 | Singles Match Play | 4 |
| R3 | Greensomes (Modified Alt. Shot) | 2 |
""")
    st.markdown("**Total: 8 matches · 8 points available**")
    st.divider()

    # New schedule: R1 Fourball (M1-M2), R2 Singles (M3-M6), R3 Greensomes (M7-M8)
    schedule = [
        ("R1-M1", "Fourball",   [w_list[0],w_list[1]], [k_list[0],k_list[1]]),
        ("R1-M2", "Fourball",   [w_list[2],w_list[3]], [k_list[2],k_list[3]]),
        ("R2-M3", "Singles",    [w_list[0]],           [k_list[0]]),
        ("R2-M4", "Singles",    [w_list[1]],           [k_list[1]]),
        ("R2-M5", "Singles",    [w_list[2]],           [k_list[2]]),
        ("R2-M6", "Singles",    [w_list[3]],           [k_list[3]]),
        ("R3-M7", "Greensomes", [w_list[0],w_list[1]], [k_list[0],k_list[1]]),
        ("R3-M8", "Greensomes", [w_list[2],w_list[3]], [k_list[2],k_list[3]]),
    ]

    st.markdown("**Current Pairings:**")
    if st.session_state.matches:
        round_labels_fmt = {
            "R1":"Round 1 – Fourball",
            "R2":"Round 2 – Singles",
            "R3":"Round 3 – Greensomes"
        }
        cur_round = None
        for mkey in sorted(st.session_state.matches.keys(), key=MSORT):
            mm  = st.session_state.matches[mkey]
            rnd = mkey.split("-")[0]
            if rnd != cur_round:
                cur_round = rnd
                st.markdown(f"*{round_labels_fmt.get(rnd,rnd)}*")
            pw_live = " & ".join(mm.get("players_w", [])) or "TBD"
            pk_live = " & ".join(mm.get("players_k", [])) or "TBD"
            st.markdown(f"- **{mkey}**: {pw_live} vs {pk_live}")
    else:
        st.info("No matches created yet — create matches below first.")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Create All 8 Matches", use_container_width=True):
            new_matches = {}
            for key, fmt, pw, pk in schedule:
                ex = st.session_state.matches.get(key, {})
                new_matches[key] = {
                    "format":fmt,"players_w":pw,"players_k":pk,
                    "scores_w":ex.get("scores_w",[0]*18),
                    "scores_k":ex.get("scores_k",[0]*18),
                    "pts_w":ex.get("pts_w",0.0),"pts_k":ex.get("pts_k",0.0),
                }
            st.session_state.matches = new_matches
            db.child("matches").set(new_matches)
            st.success("✅ All 8 matches created & synced!")
            st.rerun()
    with col2:
        if st.button("🗑️ Reset All Scores", use_container_width=True):
            for key in st.session_state.matches:
                st.session_state.matches[key].update(
                    {"scores_w":[0]*18,"scores_k":[0]*18,"pts_w":0.0,"pts_k":0.0})
            db.child("matches").set(st.session_state.matches)
            st.session_state.player_points = {}
            db.child("player_points").set({})
            st.success("Scores reset!")
            st.rerun()

# ══════════════════════════════════════════════
# TAB 2 – PLAYERS & PAIRINGS
# ══════════════════════════════════════════════
with tab_players:
    st.subheader("👥 Team Names & Players")
    tw_tmp, tk_tmp, wl_tmp, kl_tmp = get_teams()

    col_tw, col_tk = st.columns(2)
    with col_tw:
        tw_input = st.text_input("🌺 Warner (Pink) team name", tw_tmp, key="team_w_name")
    with col_tk:
        tk_input = st.text_input("🌿 Kent (Green) team name", tk_tmp, key="team_k_name")
    st.divider()

    col_w, col_k = st.columns(2)
    with col_w:
        st.markdown(f"<span class='warner'>🌺 {tw_input} Players</span>", unsafe_allow_html=True)
        w_inputs = [
            st.text_input(f"Player {i+1}", wl_tmp[i] if i < len(wl_tmp) else f"W{i+1}", key=f"wp_tab_{i}")
            for i in range(4)
        ]
    with col_k:
        st.markdown(f"<span class='kent'>🌿 {tk_input} Players</span>", unsafe_allow_html=True)
        k_inputs = [
            st.text_input(f"Player {i+1}", kl_tmp[i] if i < len(kl_tmp) else f"K{i+1}", key=f"kp_tab_{i}")
            for i in range(4)
        ]

    if st.button("💾 Save Player Names", use_container_width=True):
        st.session_state.players     = {tw_input: w_inputs, tk_input: k_inputs}
        st.session_state.warner_name = tw_input
        st.session_state.kent_name   = tk_input
        db.child("players").set(st.session_state.players)
        db.child("warner_name").set(tw_input)
        db.child("kent_name").set(tk_input)
        st.success("✅ Player names saved & synced!")
        st.rerun()

    st.divider()
    st.subheader("🔀 Match Pairings")
    st.markdown("Adjust who plays in each match, then tap Save.")

    if not st.session_state.matches:
        st.info("No matches yet – go to ⚙️ Format and create matches first.")
    else:
        team_w_p, team_k_p, w_list_p, k_list_p = get_teams()
        round_labels_p = {
            "R1":"Round 1 – Fourball",
            "R2":"Round 2 – Singles",
            "R3":"Round 3 – Greensomes"
        }
        current_round = None
        for key in sorted(st.session_state.matches.keys(), key=MSORT):
            m   = st.session_state.matches[key]
            fmt = m["format"]
            rnd = key.split("-")[0]
            if rnd != current_round:
                current_round = rnd
                st.markdown(f"##### {round_labels_p.get(rnd,rnd)}")
            st.markdown(f"**{key}** · {fmt}")
            if fmt == "Singles":
                col_a, col_b = st.columns(2)
                with col_a:
                    cur_w = m.get("players_w",[w_list_p[0]])[0]
                    sel_w = st.selectbox(f"🌺 {team_w_p}", w_list_p,
                        index=w_list_p.index(cur_w) if cur_w in w_list_p else 0,
                        key=f"pair_w_{key}")
                with col_b:
                    cur_k = m.get("players_k",[k_list_p[0]])[0]
                    sel_k = st.selectbox(f"🌿 {team_k_p}", k_list_p,
                        index=k_list_p.index(cur_k) if cur_k in k_list_p else 0,
                        key=f"pair_k_{key}")
                if st.button(f"✅ Save {key}", key=f"savepair_{key}", use_container_width=True):
                    st.session_state.matches[key]["players_w"] = [sel_w]
                    st.session_state.matches[key]["players_k"] = [sel_k]
                    db.child("matches").child(key).update({"players_w":[sel_w],"players_k":[sel_k]})
                    st.success(f"{key}: {sel_w} vs {sel_k}")
                    st.rerun()
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    cur_pw = [p for p in m.get("players_w",[]) if p in w_list_p]
                    sel_pw = st.multiselect(f"🌺 {team_w_p} Pair", w_list_p,
                        default=cur_pw, max_selections=2, key=f"pair_w_{key}")
                with col_b:
                    cur_pk = [p for p in m.get("players_k",[]) if p in k_list_p]
                    sel_pk = st.multiselect(f"🌿 {team_k_p} Pair", k_list_p,
                        default=cur_pk, max_selections=2, key=f"pair_k_{key}")
                pw_str = " & ".join(sel_pw) if sel_pw else "–"
                pk_str = " & ".join(sel_pk) if sel_pk else "–"
                st.caption(f"{pw_str} vs {pk_str}")
                if st.button(f"✅ Save {key}", key=f"savepair_{key}", use_container_width=True):
                    if len(sel_pw)==2 and len(sel_pk)==2:
                        st.session_state.matches[key]["players_w"] = sel_pw
                        st.session_state.matches[key]["players_k"] = sel_pk
                        db.child("matches").child(key).update({"players_w":sel_pw,"players_k":sel_pk})
                        st.success(f"{key}: {pw_str} vs {pk_str}")
                        st.rerun()
                    else:
                        st.error("Select exactly 2 players per team.")
            st.markdown("---")

# ══════════════════════════════════════════════
# TAB 3 – ENTER SCORES
# ══════════════════════════════════════════════
with tab_scores:
    st.subheader("🏌️ Enter Scores")
    match_keys = sorted(st.session_state.matches.keys(), key=MSORT)

    if not match_keys:
        st.info("No matches yet – go to ⚙️ Format and create matches first.")
    else:
        def fmt_key(k):
            mx = st.session_state.matches[k]
            pw = " & ".join(mx.get("players_w",[]))
            pk = " & ".join(mx.get("players_k",[]))
            return f"{k} ({mx['format']}) · {pw} vs {pk}"

        selected_key = st.selectbox("Select Match", match_keys, format_func=fmt_key)
        m   = st.session_state.matches[selected_key]
        fmt = m["format"]

        pw_names  = " & ".join(m.get("players_w",[])) or team_w
        pk_names  = " & ".join(m.get("players_k",[])) or team_k
        round_key = selected_key.split("-")[0]  # R1, R2, or R3

        # Match info card
        st.markdown(f"""
        <div class='match-card'>
        <b>{selected_key}</b> · {fmt}<br>
        <span class='warner'>🌺 {team_w}:</span> <b>{pw_names}</b> &nbsp;vs&nbsp;
        <span class='kent'>🌿 {team_k}:</span> <b>{pk_names}</b>
        </div>""", unsafe_allow_html=True)

        # Ensure score lists
        saved_w = m.get("scores_w",[0]*18)
        saved_k = m.get("scores_k",[0]*18)
        if not isinstance(saved_w, list): saved_w = [0]*18
        if not isinstance(saved_k, list): saved_k = [0]*18
        while len(saved_w) < 18: saved_w.append(0)
        while len(saved_k) < 18: saved_k.append(0)

        # ── STICKY LIVE STATUS BAR ──
        live_slot = st.empty()

        def render_live(scores_w, scores_k):
            _, _, hr, st_str = calculate_match_play(scores_w, scores_k, fmt)
            played = [r for r in hr if r is not None]
            syms = hole_symbols(hr)
            status_text = st_str if played else "Not started"
            live_slot.markdown(f"""
            <div class='live-bar'>
                <span style='font-weight:700;color:#2e7d32'>⛳ Live:</span>
                <span style='font-weight:700;margin-left:0.3rem'>{status_text}</span>
                <span style='margin-left:0.5rem;font-size:0.9rem'>{syms}</span>
            </div>""", unsafe_allow_html=True)

        render_live(saved_w, saved_k)

        # ── TOP SAVE BUTTON ──
        if st.button("💾 Save Scores/Update Leaderboard", use_container_width=True,
                     key=f"save_top_{selected_key}"):
            # collect current widget values from session state
            top_w = [int(st.session_state.get(f"sw_{selected_key}_{h}", saved_w[h])) for h in range(18)]
            top_k = [int(st.session_state.get(f"sk_{selected_key}_{h}", saved_k[h])) for h in range(18)]
            pts_w, pts_k, status = do_save(selected_key, top_w, top_k, fmt)
            st.success(f"✅ {status} · {team_w} {pts_w:.1f}pt – {team_k} {pts_k:.1f}pt")
            st.rerun()

        # ── SCORE GRID HEADER with live tally ──
        tally_w = score_tally(saved_w)
        tally_k = score_tally(saved_k)

        hc, wc, kc = st.columns([1, 5, 5])
        hc.markdown("<div style='font-weight:700;font-size:0.8rem;text-align:center'>#</div>",
                    unsafe_allow_html=True)
        par_w_hdr = to_par_str(saved_w, round_key)
        par_k_hdr = to_par_str(saved_k, round_key)
        wc.markdown(
            f"<div class='score-hdr-w'>🌺 {team_w}<br>"
            f"<small>{pw_names}</small><br>"
            f"<span style='font-size:1rem;font-weight:800'>Total: {tally_w} ({par_w_hdr})</span></div>",
            unsafe_allow_html=True)
        kc.markdown(
            f"<div class='score-hdr-k'>🌿 {team_k}<br>"
            f"<small>{pk_names}</small><br>"
            f"<span style='font-size:1rem;font-weight:800'>Total: {tally_k} ({par_k_hdr})</span></div>",
            unsafe_allow_html=True)

        new_scores_w = []
        new_scores_k = []

        LABEL_HOLES = {0, 3, 6, 9, 12, 15}

        for h in range(18):
            show_label = h in LABEL_HOLES
            hc, wc, kc = st.columns([1, 5, 5])

            top_pad = "0.2rem" if show_label else "1.6rem"
            hc.markdown(
                f"<div style='text-align:center;font-weight:700;font-size:0.9rem;"
                f"padding-top:{top_pad}'>{h+1}</div>",
                unsafe_allow_html=True)

            with wc:
                if show_label:
                    tally_so_far_w = score_tally(new_scores_w)
                    status_label   = match_status_label(new_scores_w, new_scores_k)
                    status_part    = f" · {status_label}" if status_label else ""
                    st.markdown(
                        f"<div class='score-label-w'>🌺 {pw_names}{status_part} · {tally_so_far_w}</div>",
                        unsafe_allow_html=True)
                sw = st.number_input("w", min_value=0, max_value=20, step=1,
                    value=int(saved_w[h]), key=f"sw_{selected_key}_{h}",
                    label_visibility="collapsed")

            with kc:
                if show_label:
                    tally_so_far_k = score_tally(new_scores_k)
                    # Kent status is the mirror of Warner's
                    w_status = match_status_label(new_scores_w, new_scores_k)
                    if w_status == "AS" or w_status == "":
                        k_status_part = f" · {w_status}" if w_status else ""
                    elif "UP" in w_status:
                        k_status_part = f" · {w_status.replace('UP','DN')}"
                    else:
                        k_status_part = f" · {w_status.replace('DN','UP')}"
                    st.markdown(
                        f"<div class='score-label-k'>🌿 {pk_names}{k_status_part} · {tally_so_far_k}</div>",
                        unsafe_allow_html=True)
                sk = st.number_input("k", min_value=0, max_value=20, step=1,
                    value=int(saved_k[h]), key=f"sk_{selected_key}_{h}",
                    label_visibility="collapsed")

            new_scores_w.append(sw)
            new_scores_k.append(sk)

        # Update live bar
        render_live(new_scores_w, new_scores_k)

        st.divider()
        # ── BOTTOM SAVE BUTTON ──
        if st.button("💾 Save Scores/Update Leaderboard", use_container_width=True,
                     key=f"save_bot_{selected_key}"):
            pts_w, pts_k, status = do_save(selected_key, new_scores_w, new_scores_k, fmt)
            st.success(f"✅ {status} · {team_w} {pts_w:.1f}pt – {team_k} {pts_k:.1f}pt")
            st.rerun()

# ══════════════════════════════════════════════
# TAB 4 – POINTS
# ══════════════════════════════════════════════
with tab_pp:
    st.subheader("🏆 Individual Player Points")

    live_pp = {}
    all_w = set(w_list)
    all_k = set(k_list)
    for mm in st.session_state.matches.values():
        for p in mm.get("players_w", []):
            live_pp[p] = live_pp.get(p, 0.0) + float(mm.get("pts_w", 0))
        for p in mm.get("players_k", []):
            live_pp[p] = live_pp.get(p, 0.0) + float(mm.get("pts_k", 0))
    for p in list(all_w) + list(all_k):
        if p not in live_pp:
            live_pp[p] = 0.0

    if not live_pp:
        st.info("No player points yet – save some match scores first.")
    else:
        rows = []
        for player, pts in live_pp.items():
            if player in all_w:
                rows.append({"":"🌺","Player":player,"Team":team_w,"Points":float(pts)})
            elif player in all_k:
                rows.append({"":"🌿","Player":player,"Team":team_k,"Points":float(pts)})
            else:
                rows.append({"":"⚪","Player":player,"Team":"Unknown","Points":float(pts)})
        df = pd.DataFrame(rows).sort_values("Points",ascending=False).reset_index(drop=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not df.empty:
            top = df.iloc[0]
            st.markdown(f"🥇 **Top scorer: {top['Player']} ({top['Points']:.1f} pts)**")

    st.divider()
    st.markdown("**Match Results**")
    round_labels = {
        "R1":"Round 1 – Fourball",
        "R2":"Round 2 – Singles",
        "R3":"Round 3 – Greensomes"
    }
    current_round = None
    for key in sorted(st.session_state.matches.keys(), key=MSORT):
        m    = st.session_state.matches[key]
        rnd  = key.split("-")[0]
        if rnd != current_round:
            current_round = rnd
            st.markdown(f"##### {round_labels.get(rnd,rnd)}")
        pts_w  = float(m.get("pts_w",0))
        pts_k  = float(m.get("pts_k",0))
        pw_str = " & ".join(m.get("players_w",[]))
        pk_str = " & ".join(m.get("players_k",[]))
        icon   = "🌺" if pts_w > pts_k else ("🌿" if pts_k > pts_w else ("⚪" if pts_w==0.5 else "⏳"))
        sw_saved = m.get("scores_w",[0]*18)
        sk_saved = m.get("scores_k",[0]*18)
        if not isinstance(sw_saved, list): sw_saved = [0]*18
        if not isinstance(sk_saved, list): sk_saved = [0]*18
        tally_w = score_tally(sw_saved)
        tally_k = score_tally(sk_saved)
        _, _, _, status = calculate_match_play(sw_saved, sk_saved, m.get("format",""))
        # Show score tallies alongside result
        rk = key.split("-")[0]
        par_w_res = to_par_str(sw_saved, rk)
        par_k_res = to_par_str(sk_saved, rk)
        w_score_str = f"**{tally_w}** ({par_w_res})" if tally_w else "–"
        k_score_str = f"**{tally_k}** ({par_k_res})" if tally_k else "–"
        tally_str = f" · {pw_str} {w_score_str} – {pk_str} {k_score_str}" if (tally_w or tally_k) else ""
        st.markdown(f"{icon} **{key}**: {pw_str} vs {pk_str} · *{status}* · **{pts_w:.1f}–{pts_k:.1f}**{tally_str}")

st.divider()
st.caption("⛳ Live sync via Firebase · 2026 Ryder Cup")
