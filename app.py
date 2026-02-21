import requests
import streamlit as st

try:
    API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")
except Exception:
    API_BASE = "http://localhost:8000"

st.markdown(
    """
    <style>
      :root {
        --gf-blue: #1a73e8;
        --gf-text: #202124;
        --gf-subtle: #5f6368;
        --gf-bg: #f8f9fa;
        --gf-card: #ffffff;
        --gf-border: #dadce0;
      }

      .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: var(--gf-bg) !important;
      }

      .block-container {
        max-width: 1120px;
        padding-top: 1.2rem;
      }

      [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid var(--gf-border);
      }

      h1, h2, h3, h4, p, label, .stCaption, .stMarkdown {
        color: var(--gf-text) !important;
      }

      .hero {
        background: var(--gf-card);
        border: 1px solid var(--gf-border);
        border-radius: 24px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 1px 2px rgba(60,64,67,.15);
      }

      .hero-title {
        color: var(--gf-text);
        font-size: 1.25rem;
        font-weight: 500;
        margin-bottom: 4px;
      }

      .hero-sub {
        color: var(--gf-subtle);
        font-size: .92rem;
      }

      .stButton > button, .stFormSubmitButton > button {
        border-radius: 999px !important;
        border: 1px solid var(--gf-blue) !important;
        background: var(--gf-blue) !important;
        color: #fff !important;
        font-weight: 500;
      }

      .stButton > button:hover, .stFormSubmitButton > button:hover {
        background: #1765cc !important;
        border-color: #1765cc !important;
      }

      [data-testid="stMetric"] {
        background: var(--gf-card);
        border: 1px solid var(--gf-border);
        border-radius: 16px;
        padding: 10px;
        box-shadow: 0 1px 2px rgba(60,64,67,.10);
      }

      [data-testid="stVerticalBlock"] div[data-testid="stExpander"] {
        border: 1px solid var(--gf-border);
        border-radius: 14px;
        background: #fff;
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


st.markdown(
    """
    <div class="hero">
      <div class="hero-title">PointsTrip Optimizer</div>
      <div class="hero-sub">Compare point-driven trip options by out-of-pocket cost, CPP, and booking friction.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "bundle" not in st.session_state:
    st.session_state.bundle = None
if "api_error" not in st.session_state:
    st.session_state.api_error = None

st.markdown("### Search")
with st.form("trip_form"):
    airport_label_to_code = {
        "Washington Dulles (IAD)": "IAD",
        "Washington Reagan National (DCA)": "DCA",
        "Baltimore/Washington (BWI)": "BWI",
    }

    search_c1, search_c2, search_c3, search_c4 = st.columns([2.3, 1.6, 1.2, 1.0])
    with search_c1:
        selected_origin_labels = st.multiselect(
            "From",
            list(airport_label_to_code.keys()),
            default=["Washington Dulles (IAD)", "Washington Reagan National (DCA)"],
        )
        origins = [airport_label_to_code[x] for x in selected_origin_labels]
    with search_c2:
        date_c1, date_c2 = st.columns(2)
        with date_c1:
            start = st.date_input("Depart")
        with date_c2:
            end = st.date_input("Return")
    with search_c3:
        nights = st.slider("Nights", 3, 10, 5)
        travelers = st.slider("Travelers", 1, 6, 2)
    with search_c4:
        run = st.form_submit_button("Search", use_container_width=True)

    st.markdown("#### Filters")
    f1, f2, f3 = st.columns(3)
    with f1:
        max_hours = st.slider("Max travel time (hours)", 4.0, 16.0, 10.0)
        max_stops = st.selectbox("Stops", [0, 1, 2], index=1)
    with f2:
        vibe = st.multiselect(
            "Destination style",
            ["warm beach", "south america", "eastern europe beach"],
            default=["warm beach"],
            help="Used for destination recommendation filtering.",
        )
    with f3:
        mr = st.number_input("Amex MR", min_value=0, value=100000, step=1000)
        cap1 = st.number_input("Capital One", min_value=0, value=100000, step=1000)
        marriott = st.number_input("Marriott", min_value=0, value=0, step=1000)

if run:
    if not origins:
        st.session_state.api_error = "Please select at least one origin airport."
        st.session_state.bundle = None
    elif end < start:
        st.session_state.api_error = "End date must be on or after start date."
        st.session_state.bundle = None
    else:
        st.session_state.api_error = None
        payload = {
            "origins": origins,
            "date_window_start": str(start),
            "date_window_end": str(end),
            "duration_nights": nights,
            "travelers": travelers,
            "vibe_tags": vibe,
            "constraints": {
                "max_travel_hours": max_hours,
                "max_stops": int(max_stops),
                "nonstop_preferred": max_stops == 0,
            },
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
                rec = requests.post(
                    f"{API_BASE}/v1/recommendations/generate",
                    json={"trip_search_id": trip["id"]},
                    timeout=30,
                )
                rec.raise_for_status()
                st.session_state.bundle = rec.json()
        except Exception as e:
            st.session_state.api_error = f"API error: {e}"
            st.session_state.bundle = None

if st.session_state.api_error:
    st.error(st.session_state.api_error)

bundle = st.session_state.bundle
if not bundle:
    st.info("Use the left panel to generate a polished list of options and booking playbooks.")
else:
    options = bundle.get("options", [])
    st.success(f"Found {len(options)} candidate option(s).")
    st.caption(
        f"Filters: up to {int(max_stops)} stop(s) · max {max_hours:.0f}h · vibes: {', '.join(vibe) if vibe else 'any'}"
    )

    tiles = bundle.get("winner_tiles", {})
    st.markdown("### Winner Highlights")
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Best OOP", pretty_option_id(tiles.get("best_oop", "-")))
    t2.metric("Best CPP", pretty_option_id(tiles.get("best_cpp", "-")))
    t3.metric("Best Business", pretty_option_id(tiles.get("best_business", "-")))
    t4.metric("Best Balanced", pretty_option_id(tiles.get("best_balanced", "-")))

    destination_names = {
        "CUN": "Cancún (CUN)",
        "PUJ": "Punta Cana (PUJ)",
        "NAS": "Nassau (NAS)",
        "SDQ": "Santo Domingo (SDQ)",
        "LIS": "Lisbon (LIS)",
        "ATH": "Athens (ATH)",
    }

    st.markdown("### Compare Options")
    compare_ids = st.multiselect(
        "Select up to 3 options",
        options=[o["id"] for o in options],
        format_func=pretty_option_id,
        max_selections=3,
    )
    if compare_ids:
        selected = [o for o in options if o["id"] in compare_ids]
        st.dataframe(
            [
                {
                    "Option": pretty_option_id(o["id"]),
                    "Destination": destination_names.get(o["destination"], o["destination"]),
                    "OOP": round(o["oop_total"], 2),
                    "Flight CPP": o.get("cpp_flight"),
                    "Hotel CPP": o.get("cpp_hotel"),
                    "Blended CPP": o.get("cpp_blended_capped"),
                    "Score": round(o.get("score_final", 0), 3),
                    "Hotel Mode": o.get("hotel_booking_mode", "cash"),
                }
                for o in selected
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("### Ranked Options")
    for opt in options:
        with st.container(border=True):
            a, b, c, d = st.columns([2.2, 1, 1, 1])
            dest_label = destination_names.get(opt["destination"], opt["destination"])
            a.markdown(f"#### {pretty_option_id(opt['id'])} · {dest_label}")
            b.metric("Out-of-pocket", f"${opt['oop_total']:.0f}")
            c.metric("Flight CPP", f"{opt.get('cpp_flight', 0):.2f}¢")
            d.metric("Hotel CPP", f"{opt.get('cpp_hotel', 0):.2f}¢")

            st.caption(
                f"Blended CPP: {opt['cpp_blended_capped']:.2f}¢ · Composite score: {opt['score_final']:.3f}"
            )
            st.write("Why this ranks well:", ", ".join(opt.get("rationale", [])))
            st.caption(f"Pricing snapshot: {opt.get('as_of', '-')}")

            with st.expander("Score transparency"):
                st.json(
                    {
                        "points_breakdown": opt.get("points_breakdown", {}),
                        "friction_components": opt.get("friction_components", {}),
                        "score_components": opt.get("score_components", {}),
                        "source_timestamps": opt.get("source_timestamps", {}),
                        "marriott_points_eligible": opt.get("marriott_points_eligible", False),
                    }
                )

            with st.expander("Booking playbook"):
                if st.button(
                    f"Generate Playbook for {pretty_option_id(opt['id'])}",
                    key=f"pb-{opt['id']}",
                    use_container_width=True,
                ):
                    pb = requests.post(
                        f"{API_BASE}/v1/playbook/generate",
                        json={"option_id": opt["id"]},
                        timeout=20,
                    )
                    if pb.ok:
                        p = pb.json()
                        pc1, pc2 = st.columns(2)
                        with pc1:
                            st.markdown("**Transfer Steps**")
                            for s in p["transfer_steps"]:
                                st.write(f"- {s}")
                            st.markdown("**Warnings**")
                            for s in p["warnings"]:
                                st.write(f"- {s}")
                        with pc2:
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
                            "\n## Transfer Steps",
                            *[f"- {s}" for s in p["transfer_steps"]],
                            "\n## Booking Steps",
                            *[f"- {s}" for s in p["booking_steps"]],
                            "\n## Warnings",
                            *[f"- {s}" for s in p["warnings"]],
                            "\n## Fallbacks",
                            *[f"- {s}" for s in p["fallbacks"]],
                        ])
                        st.download_button(
                            "Download Booking Plan (.md)",
                            data=export_md,
                            file_name=f"{opt['id']}_booking_plan.md",
                            mime="text/markdown",
                            use_container_width=True,
                            key=f"dl-{opt['id']}",
                        )
                    else:
                        st.error("Could not generate playbook right now.")
