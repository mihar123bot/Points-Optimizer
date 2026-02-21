import requests
import streamlit as st

try:
    API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")
except Exception:
    API_BASE = "http://localhost:8000"

st.set_page_config(page_title="PointsTrip Optimizer", layout="wide")
st.title("PointsTrip Optimizer")
st.caption("Semi-auto points trip optimizer (MVP)")

with st.sidebar:
    st.header("Trip Search")
    origins = st.multiselect("Origins", ["IAD", "DCA", "BWI"], default=["IAD", "DCA"])
    start = st.date_input("Window Start")
    end = st.date_input("Window End")
    nights = st.slider("Duration (nights)", 3, 10, 5)
    travelers = st.slider("Travelers", 1, 6, 2)
    max_hours = st.slider("Max travel hours", 4.0, 16.0, 10.0)
    max_stops = st.selectbox("Max stops", [0, 1, 2], index=1)
    vibe = st.multiselect("Vibe tags", ["warm beach", "south america", "eastern europe beach"], default=["warm beach"])
    mr = st.number_input("Amex MR", min_value=0, value=100000)
    cap1 = st.number_input("Capital One", min_value=0, value=100000)
    marriott = st.number_input("Marriott", min_value=0, value=0)
    run = st.button("Generate Recommendations", type="primary", use_container_width=True)

if run:
    payload = {
        "origins": origins,
        "date_window_start": str(start),
        "date_window_end": str(end),
        "duration_nights": nights,
        "travelers": travelers,
        "vibe_tags": vibe,
        "constraints": {"max_travel_hours": max_hours, "max_stops": int(max_stops), "nonstop_preferred": max_stops == 0},
        "balances": [
            {"program": "MR", "balance": int(mr)},
            {"program": "CAP1", "balance": int(cap1)},
            {"program": "MARRIOTT", "balance": int(marriott)},
        ],
    }

    try:
        ts = requests.post(f"{API_BASE}/v1/trip-searches", json=payload, timeout=20)
        ts.raise_for_status()
        trip = ts.json()

        rec = requests.post(f"{API_BASE}/v1/recommendations/generate", json={"trip_search_id": trip["id"]}, timeout=30)
        rec.raise_for_status()
        bundle = rec.json()
    except Exception as e:
        st.error(f"API error: {e}")
        st.stop()

    st.success(f"Generated {len(bundle['options'])} options")

    tiles = bundle["winner_tiles"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Best OOP", tiles.get("best_oop", "-"))
    c2.metric("Best CPP", tiles.get("best_cpp", "-"))
    c3.metric("Best Business", tiles.get("best_business", "-"))
    c4.metric("Best Balanced", tiles.get("best_balanced", "-"))

    st.subheader("Ranked Options")
    for opt in bundle["options"]:
        with st.container(border=True):
            a, b, c = st.columns([2, 1, 1])
            a.markdown(f"### {opt['id']} · {opt['destination']}")
            b.metric("OOP", f"${opt['oop_total']:.0f}")
            c.metric("CPP blended", f"{opt['cpp_blended_capped']:.2f}¢")
            st.write("Why:", ", ".join(opt.get("rationale", [])))
            st.caption(f"As of: {opt.get('as_of', '-')}")

            if st.button(f"Generate Playbook for {opt['id']}", key=f"pb-{opt['id']}"):
                pb = requests.post(f"{API_BASE}/v1/playbook/generate", json={"option_id": opt["id"]}, timeout=20)
                if pb.ok:
                    p = pb.json()
                    st.markdown("**Transfer Steps**")
                    for s in p["transfer_steps"]:
                        st.write(f"- {s}")
                    st.markdown("**Booking Steps**")
                    for s in p["booking_steps"]:
                        st.write(f"- {s}")
                    st.markdown("**Warnings**")
                    for s in p["warnings"]:
                        st.write(f"- {s}")
                    st.markdown("**Fallbacks**")
                    for s in p["fallbacks"]:
                        st.write(f"- {s}")
                else:
                    st.error("Could not generate playbook")
else:
    st.info("Fill the search in the sidebar and click Generate Recommendations.")
