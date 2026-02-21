import os
from datetime import datetime
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.markdown(
    """
    <style>
      :root {
        --app-blue: #1a73e8;
        --app-blue-hover: #1765cc;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --bg-main: #ffffff;
        --bg-surface: #ffffff;
        --bg-subtle: #f8fafc;
        --border: #dbe2ea;
      }

      .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
        background: var(--bg-main) !important;
      }
      .block-container { max-width: 1120px; padding-top: 1.2rem; }

      h1, h2, h3, h4, h5, h6, p, label, .stCaption, .stMarkdown, div, span, li {
        color: var(--text-primary) !important;
      }
      .stCaption { color: var(--text-secondary) !important; }

      .hero {
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 12px;
      }

      .steps { display:flex; gap:8px; margin: 8px 0 20px 0; flex-wrap: wrap; }
      .step-pill { border:1px solid var(--border); border-radius:999px; padding:6px 12px; font-size:12px; color:var(--text-secondary); background:#fff; }
      .step-pill.active { border-color: var(--app-blue); color: var(--app-blue); background:#eff6ff; }

      .badge { display:inline-block; border-radius:999px; padding:2px 8px; font-size:11px; font-weight:600; margin-right:6px; border:1px solid transparent; }
      .badge-live { background:#e8f5e9; color:#166534; border-color:#bbf7d0; }
      .badge-est { background:#fff7ed; color:#9a3412; border-color:#fed7aa; }
      .badge-best { background:#eff6ff; color:#1d4ed8; border-color:#bfdbfe; }

      .chip { border:1px solid var(--border); border-radius:999px; padding:4px 10px; font-size:12px; color:var(--text-secondary); background: var(--bg-subtle); display:inline-block; margin-right:6px; }

      .stButton > button, .stFormSubmitButton > button {
        border-radius: 999px !important;
        border: 1px solid var(--app-blue) !important;
        background: var(--app-blue) !important;
        color: #ffffff !important;
        font-weight: 500;
      }
      .stButton > button:hover, .stFormSubmitButton > button:hover {
        background: var(--app-blue-hover) !important;
        border-color: var(--app-blue-hover) !important;
      }

      [data-testid="stVerticalBlock"] div[data-testid="stContainer"] {
        border-radius: 14px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def pretty_option_id(option_id: str) -> str:
    if not option_id:
        return "-"
    tail = option_id.split("-")[-1]
    return f"Option {tail}" if tail.isdigit() else option_id


def render_steps(step: str):
    states = {
        "search": ("active", "", ""),
        "options": ("", "active", ""),
        "playbook": ("", "", "active"),
    }
    s = states.get(step, ("active", "", ""))
    st.markdown(
        f"""
        <div class="steps">
          <span class="step-pill {s[0]}">1 · Search</span>
          <span class="step-pill {s[1]}">2 · Best Options</span>
          <span class="step-pill {s[2]}">3 · Playbook</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mode_badge(label: str, mode: str) -> str:
    cls = "badge-live" if mode == "LIVE" else "badge-est"
    return f"<span class='badge {cls}'>{label}: {mode}</span>"


def summarize_why(opt: dict) -> list[str]:
    out = []
    rationale = opt.get("rationale", [])
    if rationale:
        out.append(rationale[0])
    strategy = opt.get("points_strategy", "none")
    pb = opt.get("points_breakdown", {})
    if strategy == "flight":
        out.append(f"Uses points on flights (CPP {pb.get('flight_cpp', 0):.2f}¢)")
    elif strategy == "hotel":
        out.append(f"Uses points on hotels (CPP {pb.get('hotel_cpp', 0):.2f}¢)")
    if opt.get("award_mode") == "LIVE":
        out.append("Awards inventory validated live")
    return out[:2]


def estimate_points_used(opt: dict) -> str:
    pb = opt.get("points_breakdown", {})
    strategy = opt.get("points_strategy", "none")
    if strategy == "flight":
        return f"{int(pb.get('flight_points', 0)):,} flight points"
    if strategy == "hotel":
        return f"{int(pb.get('hotel_points', 0)):,} hotel points"
    return "Cash only"


def estimate_savings_line(opt: dict) -> str:
    pb = opt.get("points_breakdown", {})
    strategy = opt.get("points_strategy", "none")
    if strategy == "flight":
        savings = float(pb.get("flight_points", 0)) * float(pb.get("flight_cpp", 0)) / 100.0
    elif strategy == "hotel":
        savings = float(pb.get("hotel_points", 0)) * float(pb.get("hotel_cpp", 0)) / 100.0
    else:
        savings = 0.0
    return f"You save ~${savings:,.0f} vs cash"


def fetch_playbook(option_id: str, strategy_override: str | None = None):
    payload = {"option_id": option_id}
    if strategy_override:
        payload["points_strategy_override"] = strategy_override
    pb = requests.post(f"{API_BASE}/v1/playbook/generate", json=payload, timeout=20)
    if not pb.ok:
        return None
    return pb.json()


def render_search():
    st.markdown("### Search Trips")
    with st.form("trip_form"):
        airport_label_to_code = {
            "Washington Dulles (IAD)": "IAD",
            "Washington Reagan National (DCA)": "DCA",
            "Baltimore/Washington (BWI)": "BWI",
        }

        ctl_c1, ctl_c2, ctl_c3, ctl_c4 = st.columns([1.2, 1.0, 1.0, 1.0])
        with ctl_c1:
            trip_type = st.selectbox("Trip type", ["Round trip", "One way"], index=0)
        with ctl_c2:
            travelers = st.selectbox("Travelers", [1, 2, 3, 4, 5, 6], index=1)
        with ctl_c3:
            cabin = st.selectbox("Cabin", ["economy", "premium_economy", "business", "first"], index=0)
        with ctl_c4:
            nights = st.slider("Nights", 3, 10, 5)

        route_c1, route_mid, route_c2 = st.columns([1.45, 0.2, 1.45])
        with route_c1:
            selected_origin_labels = st.multiselect(
                "From",
                list(airport_label_to_code.keys()),
                default=["Washington Dulles (IAD)", "Washington Reagan National (DCA)"],
            )
            origins = [airport_label_to_code[x] for x in selected_origin_labels]
        with route_mid:
            st.markdown("<div style='text-align:center; padding-top:2.1rem; color:#64748b; font-size:1.4rem;'>⇄</div>", unsafe_allow_html=True)
        with route_c2:
            destination_hint = st.text_input("To destination (optional)", placeholder="e.g., Cancun, Lisbon, CUN")

        date_c1, date_c2, date_c3 = st.columns([1.2, 1.2, 1.0])
        with date_c1:
            start = st.date_input("Depart")
        with date_c2:
            end = st.date_input("Return")
        with date_c3:
            run = st.form_submit_button("Search Trips", use_container_width=True)

        st.markdown("#### Reward Points Optimization")
        f1, f2, f3 = st.columns(3)
        with f1:
            max_hours = st.slider("Max travel time (hours)", 4, 16, 10, step=1)
            max_stops = st.selectbox("Stops", [0, 1, 2], index=1)
        with f2:
            vibe = st.multiselect("Destination style", ["warm beach", "south america", "eastern europe beach", "beach", "warm"], default=["warm beach"])
        with f3:
            mr = st.number_input("Amex MR", min_value=0, value=100000, step=1000)
            cap1 = st.number_input("Capital One", min_value=0, value=100000, step=1000)
            marriott = st.number_input("Marriott", min_value=0, value=0, step=1000)

    if not run:
        return

    if not origins:
        st.session_state.api_error = "Please select at least one origin airport."
        st.session_state.bundle = None
        return
    if trip_type == "Round trip" and end < start:
        st.session_state.api_error = "Return date must be on or after departure date."
        st.session_state.bundle = None
        return

    st.session_state.api_error = None
    preferred_destinations = [x.strip() for x in destination_hint.split(",") if x.strip()] if destination_hint else []
    payload = {
        "origins": origins,
        "date_window_start": str(start),
        "date_window_end": str(end if trip_type == "Round trip" else start),
        "duration_nights": nights,
        "travelers": int(travelers),
        "cabin_preference": cabin,
        "vibe_tags": vibe,
        "preferred_destinations": preferred_destinations,
        "constraints": {"max_travel_hours": max_hours, "max_stops": int(max_stops), "nonstop_preferred": max_stops == 0},
        "balances": [
            {"program": "MR", "balance": int(mr)},
            {"program": "CAP1", "balance": int(cap1)},
            {"program": "MARRIOTT", "balance": int(marriott)},
        ],
    }

    try:
        with st.status("Searching trips...", expanded=True) as status:
            status.write("Step 1/3: saving trip search")
            ts = requests.post(f"{API_BASE}/v1/trip-searches", json=payload, timeout=20)
            ts.raise_for_status()
            trip = ts.json()

            status.write("Step 2/3: fetching and ranking options")
            rec = requests.post(f"{API_BASE}/v1/recommendations/generate", json={"trip_search_id": trip["id"]}, timeout=30)
            if rec.status_code == 422:
                st.session_state.api_error = "No options matched your filters. Try allowing 1 stop, increasing max travel time, or broadening destination style."
                st.session_state.bundle = None
                return

            rec.raise_for_status()
            st.session_state.bundle = rec.json()
            status.write("Step 3/3: preparing decision view")
            status.update(label="Search complete", state="complete")
            st.session_state.step = "options"
    except Exception as e:
        st.session_state.api_error = f"API error: {e}"
        st.session_state.bundle = None


def render_options(bundle: dict):
    destination_names = {
        "CUN": "Cancún (CUN)", "PUJ": "Punta Cana (PUJ)", "NAS": "Nassau (NAS)",
        "SJD": "Los Cabos (SJD)", "YVR": "Vancouver (YVR)", "EZE": "Buenos Aires (EZE)",
        "LIM": "Lima (LIM)", "CDG": "Paris (CDG)", "FCO": "Rome (FCO)", "LHR": "London (LHR)",
        "KEF": "Reykjavik (KEF)", "ATH": "Athens (ATH)", "HND": "Tokyo (HND)", "BKK": "Bangkok (BKK)",
    }

    options = bundle.get("options", [])
    if not options:
        st.info("No options yet. Run search first.")
        return

    live_count = sum(1 for o in options if o.get("api_mode") == "live")
    if live_count > 0:
        st.success(f"API Mode: LIVE ({live_count}/{len(options)} options)")
    else:
        st.warning("API Mode: FALLBACK (estimated components present)")

    cache_mode = bundle.get("winner_tiles", {}).get("_meta_cache")
    if cache_mode:
        st.caption(f"Performance: {cache_mode}")

    ui_mode = st.radio("Mode", options=["Simple", "Nerd"], index=0, horizontal=True)
    st.markdown("### Best Options")

    best_value_id = bundle.get("winner_tiles", {}).get("best_balanced")
    top3 = options[:3]

    for opt in top3:
        with st.container(border=True):
            dest_label = destination_names.get(opt.get("destination"), opt.get("destination"))
            best_badge = '<span class="badge badge-best">BEST VALUE</span>' if opt.get("id") == best_value_id else ""
            award_cls = "badge-live" if opt.get("award_mode") == "LIVE" else "badge-est"
            award_txt = opt.get("award_mode", "ESTIMATED")
            as_of = opt.get("award_details", {}).get("retrieved_at") or opt.get("as_of", "-")
            as_of_short = as_of[11:16] if isinstance(as_of, str) and len(as_of) > 16 else as_of

            st.markdown(
                f"**{pretty_option_id(opt.get('id'))} · {dest_label}** "
                f"{best_badge}<span class='badge {award_cls}'>AWARDS: {award_txt}</span>"
                f"<span class='badge badge-est'>As of {as_of_short}</span>",
                unsafe_allow_html=True,
            )

            p1, p2 = st.columns(2)
            p1.metric("Total OOP", f"${opt.get('oop_total', 0):.0f}")
            p2.metric("Points Used", estimate_points_used(opt))

            # Time display: no mystery formula.
            route_time = opt.get("award_details", {}).get("duration_hours")
            if route_time is None:
                route_time_text = "~10h (estimated)"
            else:
                route_time_text = f"{float(route_time):.1f}h"

            st.markdown(
                f"<span class='chip'>CPP: {opt.get('cpp_blended_capped', 0):.2f}¢</span>"
                f"<span class='chip'>Stops: {int(opt.get('friction_components', {}).get('stops_penalty', 0) / 2)}</span>"
                f"<span class='chip'>Time: {route_time_text}</span>",
                unsafe_allow_html=True,
            )

            why = summarize_why(opt)
            if why:
                for w in why:
                    st.write(f"- {w}")
            st.caption(estimate_savings_line(opt))

            st.markdown(
                f"{mode_badge('Flights', opt.get('cash_flights_mode', 'ESTIMATED'))}"
                f"{mode_badge('Hotels', opt.get('cash_hotels_mode', 'ESTIMATED'))}"
                f"{mode_badge('Awards', opt.get('award_mode', 'ESTIMATED'))}",
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns(3)
            if c1.button("Open playbook", key=f"open-{opt['id']}", use_container_width=True):
                st.session_state.selected_option_id = opt["id"]
                st.session_state.step = "playbook"

            if c2.button("Validate", key=f"val-{opt['id']}", use_container_width=True):
                st.session_state[f"show_validate_{opt['id']}"] = not st.session_state.get(f"show_validate_{opt['id']}", False)

            with c3:
                with st.expander("Details"):
                    st.write("-", "\n- ".join(opt.get("rationale", [])))
                    if ui_mode == "Nerd":
                        st.json({
                            "points_breakdown": opt.get("points_breakdown", {}),
                            "friction_components": opt.get("friction_components", {}),
                            "score_components": opt.get("score_components", {}),
                            "source_timestamps": opt.get("source_timestamps", {}),
                            "source_labels": opt.get("source_labels", {}),
                            "award_details": opt.get("award_details", {}),
                            "raw": opt,
                        })

            if st.session_state.get(f"show_validate_{opt['id']}", False):
                with st.expander("Validate this award", expanded=True):
                    ad = opt.get("award_details", {})
                    st.write(f"Program: {ad.get('program', '-')}")
                    st.write(f"Route: {opt.get('destination', '-')}")
                    st.write(f"Date: {st.session_state.get('last_search_date', '-')}")
                    st.write(f"Cabin: {ad.get('cabin', '-')}")
                    points_val = ad.get('points')
                    points_txt = f"{int(points_val):,}" if isinstance(points_val, (int, float)) else str(points_val or "-")
                    st.write(f"Points + taxes/fees: {points_txt} + ${float(ad.get('taxes_fees',0)):.2f}")
                    for step in opt.get("validation_steps", []):
                        st.write(f"- {step}")
                    if ad.get("source_url"):
                        st.write(f"Source: {ad.get('source_url')}")
                    st.caption(f"Retrieved: {ad.get('retrieved_at', opt.get('as_of', '-'))}")


def render_playbook_page(bundle: dict):
    options = bundle.get("options", []) if bundle else []
    selected_id = st.session_state.get("selected_option_id")
    selected = next((o for o in options if o.get("id") == selected_id), None)

    st.markdown("### Playbook")
    if not selected:
        st.info("Choose an option from Step 2 first.")
        if st.button("Back to options"):
            st.session_state.step = "options"
        return

    st.write(f"**{pretty_option_id(selected.get('id'))} · {selected.get('destination')}**")
    st.caption(
        f"OOP ${selected.get('oop_total', 0):.0f} · Points {estimate_points_used(selected)} · "
        f"Modes: F {selected.get('cash_flights_mode','ESTIMATED')} / H {selected.get('cash_hotels_mode','ESTIMATED')} / A {selected.get('award_mode','ESTIMATED')}"
    )

    alternates = selected.get("points_breakdown", {}).get("points_strategy_alternates", [])
    strategy_override = None
    if alternates:
        strategy_override = st.radio(
            "Scenario",
            options=alternates,
            horizontal=True,
            format_func=lambda x: "Use points on flights" if x == "flight" else "Use points on hotels",
        )

    key = f"pb::{selected_id}::{strategy_override or 'default'}"
    if key not in st.session_state:
        st.session_state[key] = fetch_playbook(selected_id, strategy_override)

    p = st.session_state.get(key)
    if not p:
        st.error("Could not load playbook.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Transfer steps**")
        for s in p.get("transfer_steps", []):
            st.write(f"- {s}")
        st.markdown("**Warnings**")
        for s in p.get("warnings", []):
            st.write(f"- {s}")
    with c2:
        st.markdown("**Booking steps**")
        for s in p.get("booking_steps", []):
            st.write(f"- {s}")
        st.markdown("**Fallbacks**")
        for s in p.get("fallbacks", []):
            st.write(f"- {s}")

    export_md = "\n".join([
        f"# {pretty_option_id(selected.get('id'))} · {selected.get('destination')}",
        f"- Out-of-pocket: ${selected.get('oop_total', 0):.2f}",
        f"- Points used: {estimate_points_used(selected)}",
        "\n## Transfer Steps", *[f"- {s}" for s in p.get("transfer_steps", [])],
        "\n## Booking Steps", *[f"- {s}" for s in p.get("booking_steps", [])],
        "\n## Warnings", *[f"- {s}" for s in p.get("warnings", [])],
        "\n## Fallbacks", *[f"- {s}" for s in p.get("fallbacks", [])],
    ])
    st.download_button("Download playbook (.md)", data=export_md, file_name=f"{selected_id}_booking_plan.md", mime="text/markdown", use_container_width=True)

    if st.button("Back to options"):
        st.session_state.step = "options"


# --- App State ---
if "step" not in st.session_state:
    st.session_state.step = "search"
if "selected_option_id" not in st.session_state:
    st.session_state.selected_option_id = None
if "bundle" not in st.session_state:
    st.session_state.bundle = None
if "api_error" not in st.session_state:
    st.session_state.api_error = None

st.markdown(
    """
    <div class="hero">
      <div style="font-size:1.25rem;font-weight:600;">PointsTrip Optimizer</div>
      <div style="font-size:.92rem;color:#475569;">Simple, credible trip decisions with exportable playbooks.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_steps(st.session_state.step)
render_search()

if st.session_state.api_error:
    st.error(st.session_state.api_error)

if st.session_state.step == "search":
    st.info("Run a search to move to Step 2.")
elif st.session_state.step == "options":
    render_options(st.session_state.bundle or {})
elif st.session_state.step == "playbook":
    render_playbook_page(st.session_state.bundle or {})
