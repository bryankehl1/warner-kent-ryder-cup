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
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Warner vs Kent Ryder Cup",
    page_icon="⛳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# PINK  = Warner = #FF6B7A
# GREEN = Kent   = #1a7a6e

st.markdown("""
<style>
    /* ══ FORCE LIGHT MODE ══ */
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"],
    [data-testid="stMain"],
    [data-testid="block-container"],
    [data-testid="stVerticalBlock"] {
        background-color: #f5f7f5 !important;
        color: #1a1a1a !important;
    }
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    @media (prefers-color-scheme: dark) {
        html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stApp"],
        [data-testid="stMain"],
        [data-testid="block-container"],
        [data-testid="stVerticalBlock"] {
            background-color: #f5f7f5 !important;
            color: #1a1a1a !important;
        }
        [data-testid="stSidebar"],
        [data-testid="stSidebarContent"] {
            background-color: #ffffff !important;
            color: #1a1a1a !important;
        }
        p, h1, h2, h3, h4, h5, h6, span, label {
            color: #1a1a1a !important;
        }
        .stNumberInput input, .stTextInput input {
            background-color: #ffffff !important;
            color: #1a1a1a !important;
        }
        .stSelectbox > div > div {
            background-color: #ffffff !important;
            color: #1a1a1a !important;
        }
    }

    /* ══ BASE ══ */
    .stApp { padding: 0.5rem; }

    /* ══ BUTTONS ══ */
    .stButton > button {
        width: 100%; min-height: 2.8rem; font-size: 1rem;
        border-radius: 10px; font-weight: 600;
        color: #ffffff !important;
        background-color: #2e7d32 !important;
        border: none;
    }
    .stButton > button:hover  { background-color: #1b5e20 !important; }
    .stButton > button:active { background-color: #1b5e20 !important; }

    /* ══ NUMBER INPUTS – compact ══ */
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

    /* ══ SCORE INPUT COLOURS – by key ══ */
    /* Warner inputs (keys start with sw_) → pink border + tint */
    [data-testid*="sw_"] input {
        border: 2.5px solid #FF6B7A !important;
        background-color: #fff5f6 !important;
        border-radius: 8px !important;
        color: #1a1a1a !important;
    }
    /* Kent inputs (keys start with sk_) → green border + tint */
    [data-testid*="sk_"] input {
        border: 2.5px solid #1a7a6e !important;
        background-color: #f0f8f6 !important;
        border-radius: 8px !important;
        color: #1a1a1a !important;
    }

    /* ══ MATCH CARD ══ */
    .match-card {
        background: white; border-radius: 12px;
        padding: 0.7rem 1rem; margin: 0.3rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        font-size: 0.92rem; line-height: 1.5;
    }

    /* ══ STICKY LIVE STATUS BAR ══ */
    .live-bar {
        position: sticky;
        top: 0;
        z-index: 999;
        background: #ffffff;
        border-left: 4px solid #2e7d32;
        border-radius: 0 10px 10px 0;
        padding: 0.45rem 0.8rem;
        margin-bottom: 0.6rem;
        box-shadow: 0 3px 10px rgba(0,0,0,0.12);
        font-size: 0.88rem;
    }

    /* ══ SCORE GRID HEADER ══ */
    .score-hdr-w {
        background: #fff0f3;
        border: 2px solid #FF6B7A;
        border-radius: 8px;
        padding: 0.2rem 0.4rem;
        font-size: 0.78rem;
        font-weight: 700;
        color: #FF6B7A;
        text-align: center;
    }
    .score-hdr-k {
        background: #f0f8f6;
        border: 2px solid #1a7a6e;
        border-radius: 8px;
        padding: 0.2rem 0.4rem;
        font-size: 0.78rem;
        font-weight: 700;
        color: #1a7a6e;
        text-align: center;
    }

    /* ══ FLOWER LABEL pill – sits inline above input on mobile ══ */
    .pill-w {
        display: inline-block;
        background: #FF6B7A;
        color: white;
        border-radius: 20px;
        padding: 0.1rem 0.5rem;
        font-size: 0.72rem;
        font-weight: 700;
        margin-bottom: 0.15rem;
        white-space: nowrap;
    }
    .pill-k {
        display: inline-block;
        background: #1a7a6e;
        color: white;
        border-radius: 20px;
        padding: 0.1rem 0.5rem;
        font-size: 0.72rem;
        font-weight: 700;
        margin-bottom: 0.15rem;
        white-space: nowrap;
    }

    /* ══ TEAM COLOURS ══ */
    .warner { color: #FF6B7A !important; font-weight: 700; }
    .kent   { color: #1a7a6e !important; font-weight: 700; }

    /* ══ LEADERBOARD ══ */
    .vs-text { text-align:center; font-size:1.1rem; color:#555; padding-top:1.2rem; }
</style>
""", unsafe_allow_html=True)

st.title("⛳ Warner vs Kent Ryder Cup")

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    for k, v in [("players",{}),("matches",{}),("player_points",{}),
                 ("firebase_loaded",False),
                 ("warner_name","Team Warner"),("kent_name","Team Kent")]:
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# ─────────────────────────────────────────────
# FIREBASE LOAD
# ─────────────────────────────────────────────
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

# Auto-repair: detect team identity from stored player key names
for _k in list(st.session_state.players.keys()):
    if "warner" in _k.lower():
        st.session_state.warner_name = _k
    elif "kent" in _k.lower():
        st.session_state.kent_name = _k

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("⛳ Warner vs Kent")
    st.markdown("Use the **👥 Players** tab to set names & pairings.")
    st.divider()
    if st.button("🔄 Refresh from Firebase"):
        st.session_state.firebase_loaded = False
        st.rerun()
    st.caption("All changes sync live via Firebase.")

team_w, team_k, w_list, k_list = get_teams()

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_setup, tab_players, tab_scores, tab_lb, tab_pp = st.tabs(
    ["⚙️ Setup","👥 Players","🏌️ Scores","🏆 Leaderboard","👤 Points"])

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

    schedule = [
        ("R1-M1","Foursomes", [w_list[0],w_list[1]], [k_list[0],k_list[1]]),
        ("R1-M2","Foursomes", [w_list[2],w_list[3]], [k_list[2],k_list[3]]),
        ("R2-M1","Fourball",  [w_list[0],w_list[1]], [k_list[0],k_list[1]]),
        ("R2-M2","Fourball",  [w_list[2],w_list[3]], [k_list[2],k_list[3]]),
        ("R3-M1","Greensomes",[w_list[0],w_list[1]], [k_list[0],k_list[1]]),
        ("R3-M2","Greensomes",[w_list[2],w_list[3]], [k_list[2],k_list[3]]),
        ("R4-M1","Singles",   [w_list[0]],           [k_list[0]]),
        ("R4-M2","Singles",   [w_list[1]],           [k_list[1]]),
        ("R4-M3","Singles",   [w_list[2]],           [k_list[2]]),
        ("R4-M4","Singles",   [w_list[3]],           [k_list[3]]),
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
                ex = st.session_state.matches.get(key, {})
                new_matches[key] = {
                    "format":fmt,"players_w":pw,"players_k":pk,
                    "scores_w":ex.get("scores_w",[0]*18),
                    "scores_k":ex.get("scores_k",[0]*18),
                    "pts_w":ex.get("pts_w",0.0),"pts_k":ex.get("pts_k",0.0),
                }
            st.session_state.matches = new_matches
            db.child("matches").set(new_matches)
            st.success("✅ All 10 matches created & synced!")
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
        st.info("No matches yet – go to ⚙️ Setup and create matches first.")
    else:
        team_w_p, team_k_p, w_list_p, k_list_p = get_teams()
        round_labels = {
            "R1":"Round 1 – Foursomes","R2":"Round 2 – Fourball",
            "R3":"Round 3 – Greensomes","R4":"Round 4 – Singles"
        }
        current_round = None
        for key in sorted(st.session_state.matches.keys()):
            m   = st.session_state.matches[key]
            fmt = m["format"]
            rnd = key.split("-")[0]
            if rnd != current_round:
                current_round = rnd
                st.markdown(f"##### {round_labels.get(rnd,rnd)}")
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
    match_keys = list(st.session_state.matches.keys())

    if not match_keys:
        st.info("No matches yet – go to ⚙️ Setup and create matches first.")
    else:
        def fmt_key(k):
            mx  = st.session_state.matches[k]
            pw = " & ".join(mx.get("players_w",[]))
            pk = " & ".join(mx.get("players_k",[]))
            return f"{k} ({mx['format']}) · {pw} vs {pk}"

        selected_key = st.selectbox("Select Match", match_keys, format_func=fmt_key)
        m   = st.session_state.matches[selected_key]
        fmt = m["format"]

        pw_names = " & ".join(m.get("players_w",[])) or team_w
        pk_names = " & ".join(m.get("players_k",[])) or team_k

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

        # ── STICKY LIVE STATUS (st.empty so it updates as scores change) ──
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

        # Show saved state immediately
        render_live(saved_w, saved_k)

        # ── SCORE GRID ──
        # Column header
        hc, wc, kc = st.columns([1, 5, 5])
        hc.markdown("<div style='font-weight:700;font-size:0.8rem;text-align:center'>#</div>",
                    unsafe_allow_html=True)
        wc.markdown(f"<div class='score-hdr-w'>🌺 {team_w}<br><small>{pw_names}</small></div>",
                    unsafe_allow_html=True)
        kc.markdown(f"<div class='score-hdr-k'>🌿 {team_k}<br><small>{pk_names}</small></div>",
                    unsafe_allow_html=True)

        new_scores_w = []
        new_scores_k = []

        for h in range(18):
            hc, wc, kc = st.columns([1, 5, 5])
            # Hole number
            hc.markdown(
                f"<div style='text-align:center;font-weight:700;font-size:0.9rem;"
                f"padding-top:0.3rem'>{h+1}</div>",
                unsafe_allow_html=True)
            # Warner score – pill label uses number_input's own label, visible on mobile
            sw = wc.number_input(
                f"🌺 W{h+1}",
                min_value=0, max_value=20, step=1,
                value=int(saved_w[h]),
                key=f"sw_{selected_key}_{h}",
                label_visibility="collapsed")
            # Kent score
            sk = kc.number_input(
                f"🌿 K{h+1}",
                min_value=0, max_value=20, step=1,
                value=int(saved_k[h]),
                key=f"sk_{selected_key}_{h}",
                label_visibility="collapsed")
            new_scores_w.append(sw)
            new_scores_k.append(sk)

        # Update live bar with current inputs
        render_live(new_scores_w, new_scores_k)

        st.divider()
        if st.button("💾 Save & Calculate Match", use_container_width=True, key=f"save_{selected_key}"):
            pts_w, pts_k, _, status = calculate_match_play(new_scores_w, new_scores_k, fmt)
            st.session_state.matches[selected_key].update({
                "scores_w":new_scores_w,"scores_k":new_scores_k,
                "pts_w":pts_w,"pts_k":pts_k
            })
            db.child("matches").child(selected_key).update({
                "scores_w":new_scores_w,"scores_k":new_scores_k,
                "pts_w":pts_w,"pts_k":pts_k
            })
            recalculate_player_points()
            st.success(f"✅ {status} · {team_w} {pts_w:.1f}pt – {team_k} {pts_k:.1f}pt")
            st.rerun()

# ══════════════════════════════════════════════
# TAB 4 – LEADERBOARD
# ══════════════════════════════════════════════
with tab_lb:
    st.subheader("🏆 Team Leaderboard")
    total_w = sum(float(m.get("pts_w",0)) for m in st.session_state.matches.values())
    total_k = sum(float(m.get("pts_k",0)) for m in st.session_state.matches.values())
    total_available = 10.0
    needed = total_available / 2 + 0.5

    col_w, col_vs, col_k = st.columns([5,2,5])
    with col_w:
        st.markdown(f"""
        <div style='background:#FF6B7A;color:white;border-radius:12px;
                    padding:0.9rem 0.5rem;text-align:center;
                    font-size:1.3rem;font-weight:bold;'>
            🌺 {team_w}<br>{total_w:.1f}
        </div>""", unsafe_allow_html=True)
    with col_vs:
        st.markdown("<div class='vs-text'>vs</div>", unsafe_allow_html=True)
    with col_k:
        st.markdown(f"""
        <div style='background:#1a7a6e;color:white;border-radius:12px;
                    padding:0.9rem 0.5rem;text-align:center;
                    font-size:1.3rem;font-weight:bold;'>
            🌿 {team_k}<br>{total_k:.1f}
        </div>""", unsafe_allow_html=True)

    st.markdown(f"**{needed:.1f} pts to win · {total_available-total_w-total_k:.1f} pts still to play**")

    if total_w >= needed:
        st.success(f"🏆 {team_w} WIN THE RYDER CUP!")
    elif total_k >= needed:
        st.success(f"🏆 {team_k} WIN THE RYDER CUP!")
    elif total_w == total_k == total_available / 2:
        st.info("🤝 It's a TIE — Cup retained by the holders!")

    st.divider()
    st.markdown("**Match Results**")
    round_labels = {"R1":"Round 1 – Foursomes","R2":"Round 2 – Fourball",
                    "R3":"Round 3 – Greensomes","R4":"Round 4 – Singles"}
    current_round = None
    for key in sorted(st.session_state.matches.keys()):
        m   = st.session_state.matches[key]
        rnd = key.split("-")[0]
        if rnd != current_round:
            current_round = rnd
            st.markdown(f"##### {round_labels.get(rnd,rnd)}")
        pts_w  = float(m.get("pts_w",0))
        pts_k  = float(m.get("pts_k",0))
        pw_str = " & ".join(m.get("players_w",[]))
        pk_str = " & ".join(m.get("players_k",[]))
        icon   = "🌺" if pts_w > pts_k else ("🌿" if pts_k > pts_w else ("⚪" if pts_w==0.5 else "⏳"))
        _, _, _, status = calculate_match_play(
            m.get("scores_w",[0]*18), m.get("scores_k",[0]*18), m.get("format",""))
        st.markdown(f"{icon} **{key}**: {pw_str} vs {pk_str} · *{status}* · **{pts_w:.1f}–{pts_k:.1f}**")

# ══════════════════════════════════════════════
# TAB 5 – PLAYER POINTS
# ══════════════════════════════════════════════
with tab_pp:
    st.subheader("👤 Individual Player Points")
    pp = st.session_state.player_points
    if not pp:
        st.info("No player points yet – save some match scores first.")
    else:
        rows = []
        for player, pts in pp.items():
            if player in w_list:
                rows.append({"":"🌺","Player":player,"Team":team_w,"Points":float(pts)})
            elif player in k_list:
                rows.append({"":"🌿","Player":player,"Team":team_k,"Points":float(pts)})
            else:
                rows.append({"":"⚪","Player":player,"Team":"Unknown","Points":float(pts)})
        df = pd.DataFrame(rows).sort_values("Points",ascending=False).reset_index(drop=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not df.empty:
            top = df.iloc[0]
            st.markdown(f"🥇 **Top scorer: {top['Player']} ({top['Points']:.1f} pts)**")

st.divider()
st.caption("⛳ Live sync via Firebase · Warner vs Kent Ryder Cup")
