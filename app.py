import os
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

      h1, h2, h3, h4, h5, h6,
      p, label, .stCaption, .stMarkdown,
      div, span, li {
        color: var(--text-primary) !important;
      }
      small, .stCaption { color: var(--text-secondary) !important; }

      .hero {
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
      }
      .hero-title { color: var(--text-primary); font-size: 1.25rem; font-weight: 600; margin-bottom: 4px; }
      .hero-sub { color: var(--text-secondary); font-size: .92rem; }

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

      [data-testid="stMetric"],
      [data-testid="stVerticalBlock"] div[data-testid="stExpander"],
      [data-testid="stDataFrame"] {
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 14px;
      }

      input, textarea, select,
      [data-baseweb="select"] > div,
      [data-baseweb="input"] > div {
        background: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border-color: var(--border) !important;
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


def render_playbook(opt: dict, dest_label: str):
    alternates = opt.get("points_breakdown", {}).get("points_strategy_alternates", [])
    selected_strategy = None
    if alternates:
        selected_strategy = st.radio(
            "Points strategy scenario",
            options=alternates,
            index=0,
            horizontal=True,
            key=f"strategy-{opt['id']}",
            format_func=lambda x: "Use points on flights" if x == "flight" else "Use points on hotels",
        )

    if st.button(f"Open Booking Plan for {pretty_option_id(opt['id'])}", key=f"pb-{opt['id']}", use_container_width=True):
        payload = {"option_id": opt["id"]}
        if selected_strategy:
            payload["points_strategy_override"] = selected_strategy
        pb = requests.post(f"{API_BASE}/v1/playbook/generate", json=payload, timeout=20)
        if not pb.ok:
            st.error("Could not generate booking plan right now.")
            return
        p = pb.json()
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Transfer Steps**")
            for s in p["transfer_steps"]:
                st.write(f"- {s}")
            st.markdown("**Warnings**")
            for s in p["warnings"]:
                st.write(f"- {s}")
        with c2:
            st.markdown("**Booking Steps**")
            for s in p["booking_steps"]:
                st.write(f"- {s}")
            st.markdown("**Fallbacks**")
            for s in p["fallbacks"]:
                st.write(f"- {s}")

        export_md = "\n".join([
            f"# {pretty_option_id(opt['id'])} · {dest_label}",
            f"- Out-of-pocket: ${opt['oop_total']:.2f}",
            f"- Flight CPP: {opt.get('cpp_flight', 0):.2f}¢",
            f"- Hotel CPP: {opt.get('cpp_hotel', 0):.2f}¢",
            "\n## Transfer Steps", *[f"- {s}" for s in p["transfer_steps"]],
            "\n## Booking Steps", *[f"- {s}" for s in p["booking_steps"]],
            "\n## Warnings", *[f"- {s}" for s in p["warnings"]],
            "\n## Fallbacks", *[f"- {s}" for s in p["fallbacks"]],
        ])
        st.download_button("Download Booking Plan (.md)", data=export_md, file_name=f"{opt['id']}_booking_plan.md", mime="text/markdown", use_container_width=True, key=f"dl-{opt['id']}")


st.markdown(
    """
    <div class="hero">
      <div class="hero-title">PointsTrip Optimizer</div>
      <div class="hero-sub">Step 1: Search trips · Step 2: Pick an option · Step 3: Execute the booking plan.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "bundle" not in st.session_state:
    st.session_state.bundle = None
if "api_error" not in st.session_state:
    st.session_state.api_error = None

st.markdown("### Step 1 · Search Trips")
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
        vibe = st.multiselect("Destination style", ["warm beach", "south america", "eastern europe beach"], default=["warm beach"])
    with f3:
        mr = st.number_input("Amex MR", min_value=0, value=100000, step=1000)
        cap1 = st.number_input("Capital One", min_value=0, value=100000, step=1000)
        marriott = st.number_input("Marriott", min_value=0, value=0, step=1000)

if run:
    if not origins:
        st.session_state.api_error = "Please select at least one origin airport."
        st.session_state.bundle = None
    elif trip_type == "Round trip" and end < start:
        st.session_state.api_error = "Return date must be on or after departure date."
        st.session_state.bundle = None
    else:
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
            with st.spinner("Building your trip options..."):
                ts = requests.post(f"{API_BASE}/v1/trip-searches", json=payload, timeout=20)
                ts.raise_for_status()
                trip = ts.json()
                rec = requests.post(f"{API_BASE}/v1/recommendations/generate", json={"trip_search_id": trip["id"]}, timeout=30)
                if rec.status_code == 422:
                    st.session_state.api_error = "No options matched your filters. Try allowing 1 stop, increasing max travel time, or broadening destination style."
                    st.session_state.bundle = None
                else:
                    rec.raise_for_status()
                    st.session_state.bundle = rec.json()
        except Exception as e:
            st.session_state.api_error = f"API error: {e}"
            st.session_state.bundle = None

if st.session_state.api_error:
    st.error(st.session_state.api_error)

bundle = st.session_state.bundle
destination_names = {
    "CUN": "Cancún (CUN)",
    "PUJ": "Punta Cana (PUJ)",
    "NAS": "Nassau (NAS)",
    "SJD": "Los Cabos (SJD)",
    "YVR": "Vancouver (YVR)",
    "EZE": "Buenos Aires (EZE)",
    "LIM": "Lima (LIM)",
    "CDG": "Paris (CDG)",
    "FCO": "Rome (FCO)",
    "LHR": "London (LHR)",
    "KEF": "Reykjavik (KEF)",
    "ATH": "Athens (ATH)",
    "HND": "Tokyo (HND)",
    "BKK": "Bangkok (BKK)",
}

if not bundle:
    st.info("Step 2 appears here after search. If no options appear, relax stops/time filters.")
else:
    options = bundle.get("options", [])
    live_count = sum(1 for o in options if o.get("api_mode") == "live")
    if live_count > 0:
        st.success(f"API Mode: LIVE ({live_count}/{len(options)} options using live provider data)")
    else:
        st.warning("API Mode: FALLBACK (using estimator/mock data). Add AMADEUS_CLIENT_ID/SECRET and optional SEATS_AERO settings to enable live award validation.")

    ui_mode = st.radio("View mode", options=["Simple", "Nerd"], index=0, horizontal=True)

    st.markdown("### Step 2 · Decision View")
    st.caption("Simple mode: top 3 options only. Use Nerd mode for full scoring and source internals.")

    top3 = options[:3]
    for opt in top3:
        with st.container(border=True):
            a, b, c, d = st.columns([2.4, 1, 1, 1])
            dest_label = destination_names.get(opt["destination"], opt["destination"])
            a.markdown(f"#### {pretty_option_id(opt['id'])} · {dest_label}")
            b.metric("Out-of-pocket", f"${opt['oop_total']:.0f}")
            c.metric("CPP", f"{opt.get('cpp_blended_capped', 0):.2f}¢")
            d.metric("Stops", opt.get("friction_components", {}).get("stops_penalty", 0) / 2)
            st.write("Why:", ", ".join(opt.get("rationale", [])))
            st.caption(
                f"Component modes — Flights: {opt.get('cash_flights_mode','ESTIMATED')} · Hotels: {opt.get('cash_hotels_mode','ESTIMATED')} · Awards: {opt.get('award_mode','ESTIMATED')}"
            )
            if opt.get("award_mode", "ESTIMATED") != "LIVE":
                st.info("Award values are estimated for this option (live award source unavailable, quota-limited, or not configured).")

            with st.expander("Validate this award"):
                for step in opt.get("validation_steps", []):
                    st.write(f"- {step}")
                award_src = opt.get("award_details", {}).get("source_url")
                if award_src:
                    st.write(f"Source link: {award_src}")
                st.caption(f"As of: {opt.get('award_details', {}).get('retrieved_at', opt.get('as_of', '-'))}")

            render_playbook(opt, dest_label)

    if ui_mode == "Nerd":
        with st.expander("Advanced Details", expanded=True):
            st.markdown("#### Compare Selected")
            compare_ids = st.multiselect("Select up to 3 options", options=[o["id"] for o in options], format_func=pretty_option_id, max_selections=3)
            if compare_ids:
                selected = [o for o in options if o["id"] in compare_ids]
                st.dataframe([
                    {
                        "Option": pretty_option_id(o["id"]),
                        "Destination": destination_names.get(o["destination"], o["destination"]),
                        "OOP": round(o["oop_total"], 2),
                        "Flight CPP": o.get("cpp_flight"),
                        "Hotel CPP": o.get("cpp_hotel"),
                        "Blended CPP": o.get("cpp_blended_capped"),
                        "Score": round(o.get("score_final", 0), 3),
                        "Flight Mode": o.get("cash_flights_mode", "ESTIMATED"),
                        "Hotel Mode": o.get("cash_hotels_mode", "ESTIMATED"),
                        "Award Mode": o.get("award_mode", "ESTIMATED"),
                    } for o in selected
                ], use_container_width=True, hide_index=True)

            st.markdown("#### Full Ranked List")
            for opt in options:
                with st.container(border=True):
                    dest_label = destination_names.get(opt["destination"], opt["destination"])
                    st.markdown(f"**{pretty_option_id(opt['id'])} · {dest_label}**")
                    st.caption(f"OOP ${opt['oop_total']:.0f} · Flight CPP {opt.get('cpp_flight',0):.2f}¢ · Hotel CPP {opt.get('cpp_hotel',0):.2f}¢")
                    st.caption(f"Modes → flights: {opt.get('cash_flights_mode','ESTIMATED')}, hotels: {opt.get('cash_hotels_mode','ESTIMATED')}, award: {opt.get('award_mode','ESTIMATED')}")
                    with st.expander("Score transparency"):
                        st.json({
                            "points_breakdown": opt.get("points_breakdown", {}),
                            "friction_components": opt.get("friction_components", {}),
                            "score_components": opt.get("score_components", {}),
                            "source_timestamps": opt.get("source_timestamps", {}),
                            "source_labels": opt.get("source_labels", {}),
                            "award_details": opt.get("award_details", {}),
                            "validation_steps": opt.get("validation_steps", []),
                            "api_mode": opt.get("api_mode", "fallback"),
                            "marriott_points_eligible": opt.get("marriott_points_eligible", False),
                        })
