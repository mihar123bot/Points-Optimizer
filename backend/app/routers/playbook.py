from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.domain.models import PlaybookResponse
from app.store import load_recommendations, load_trip_searches
from app.data.transfer_partners import (
    get_transferable_programs_for_backend,
    get_programs_for_airline,
    CARD_TO_BACKEND,
)

router = APIRouter()

# ── Transfer partner catalog ──────────────────────────────────────────────────
# Each partner entry: ratio, transfer speed, transfer URL, booking URL
TRANSFER_PARTNERS: dict[str, dict] = {
    "MR": {
        "label": "Amex Membership Rewards",
        "partners": {
            "Air France/KLM Flying Blue": {
                "ratio": "1:1", "speed": "instant",
                "transfer_url": "https://www.americanexpress.com/en-us/rewards/membership-rewards/partners/",
                "book_url": "https://www.airfranceklm.com/en/flying-blue/",
            },
            "British Airways Executive Club": {
                "ratio": "1:1", "speed": "instant",
                "transfer_url": "https://www.americanexpress.com/en-us/rewards/membership-rewards/partners/",
                "book_url": "https://www.britishairways.com/en-us/executive-club/spending-avios/on-flights",
            },
            "Singapore KrisFlyer": {
                "ratio": "1:1", "speed": "24–48 hrs",
                "transfer_url": "https://www.americanexpress.com/en-us/rewards/membership-rewards/partners/",
                "book_url": "https://www.singaporeair.com/en_UK/us/ppsclub-krisflyer/",
            },
            "ANA Mileage Club": {
                "ratio": "1:1", "speed": "2–5 days",
                "transfer_url": "https://www.americanexpress.com/en-us/rewards/membership-rewards/partners/",
                "book_url": "https://www.ana.co.jp/en/us/amc/",
            },
            "Virgin Atlantic Flying Club": {
                "ratio": "1:1", "speed": "instant",
                "transfer_url": "https://www.americanexpress.com/en-us/rewards/membership-rewards/partners/",
                "book_url": "https://www.virginatlantic.com/us/en/flying-club.html",
            },
            "Delta SkyMiles": {
                "ratio": "1:1", "speed": "instant",
                "transfer_url": "https://www.americanexpress.com/en-us/rewards/membership-rewards/partners/",
                "book_url": "https://www.delta.com/us/en/skymiles/overview",
            },
        },
    },
    "CAP1": {
        "label": "Capital One Miles",
        "partners": {
            "Air Canada Aeroplan": {
                "ratio": "1:1", "speed": "instant",
                "transfer_url": "https://www.capitalone.com/credit-cards/benefits/travel/transfer-partners/",
                "book_url": "https://www.aircanada.com/aeroplan",
            },
            "Turkish Miles&Smiles": {
                "ratio": "1:1", "speed": "instant",
                "transfer_url": "https://www.capitalone.com/credit-cards/benefits/travel/transfer-partners/",
                "book_url": "https://www.turkishairlines.com/en-us/miles-and-smiles/",
            },
            "British Airways Avios": {
                "ratio": "1:1", "speed": "instant",
                "transfer_url": "https://www.capitalone.com/credit-cards/benefits/travel/transfer-partners/",
                "book_url": "https://www.britishairways.com/en-us/executive-club/spending-avios/on-flights",
            },
            "Singapore KrisFlyer": {
                "ratio": "1:1", "speed": "24–48 hrs",
                "transfer_url": "https://www.capitalone.com/credit-cards/benefits/travel/transfer-partners/",
                "book_url": "https://www.singaporeair.com/",
            },
            "Avianca LifeMiles": {
                "ratio": "1:1", "speed": "instant",
                "transfer_url": "https://www.capitalone.com/credit-cards/benefits/travel/transfer-partners/",
                "book_url": "https://www.lifemiles.com/",
            },
        },
    },
    "MARRIOTT": {
        "label": "Marriott Bonvoy",
        "partners": {},
        "book_url": "https://www.marriott.com/rewards/",
    },
}

# ── Best booking portals by destination ───────────────────────────────────────
# Ordered by recommended priority; each entry includes tips for the user.
BOOKING_PORTALS: dict[str, list[dict]] = {
    "CDG": [
        {"name": "Air France Flying Blue", "url": "https://www.airfranceklm.com/en/flying-blue/", "program": "MR", "partner": "Air France/KLM Flying Blue", "tip": "Best option — transfer MR → Flying Blue 1:1 (instant). Book on airfranceklm.com."},
        {"name": "British Airways Avios", "url": "https://www.britishairways.com/en-us/executive-club/spending-avios/on-flights", "program": "MR", "partner": "British Airways Executive Club", "tip": "Use Avios for BA-operated CDG flights."},
    ],
    "LHR": [
        {"name": "British Airways Executive Club", "url": "https://www.britishairways.com/en-us/executive-club/spending-avios/on-flights", "program": "MR", "partner": "British Airways Executive Club", "tip": "Best for BA metal — transfer MR or CAP1 → Avios 1:1. Book on ba.com."},
        {"name": "Virgin Atlantic Flying Club", "url": "https://www.virginatlantic.com/us/en/flying-club.html", "program": "MR", "partner": "Virgin Atlantic Flying Club", "tip": "Great alternative, especially for VS-operated flights."},
    ],
    "FCO": [
        {"name": "Air France Flying Blue", "url": "https://www.airfranceklm.com/en/flying-blue/", "program": "MR", "partner": "Air France/KLM Flying Blue", "tip": "Flying Blue prices Rome well. Transfer MR instantly."},
        {"name": "British Airways Avios", "url": "https://www.britishairways.com/en-us/executive-club/spending-avios/on-flights", "program": "MR", "partner": "British Airways Executive Club"},
    ],
    "ATH": [
        {"name": "Air France Flying Blue", "url": "https://www.airfranceklm.com/en/flying-blue/", "program": "MR", "partner": "Air France/KLM Flying Blue", "tip": "Air France operates CDG–ATH, good Flying Blue pricing."},
        {"name": "British Airways Avios", "url": "https://www.britishairways.com/en-us/executive-club/spending-avios/on-flights", "program": "MR", "partner": "British Airways Executive Club"},
    ],
    "KEF": [
        {"name": "Icelandair Saga Club", "url": "https://www.icelandair.com/sagaclub/", "tip": "Book direct at icelandair.com — cash fares are often competitive vs awards."},
        {"name": "British Airways Avios", "url": "https://www.britishairways.com/en-us/executive-club/spending-avios/on-flights", "program": "MR", "partner": "British Airways Executive Club", "tip": "BA code-shares on some Icelandair routes."},
    ],
    "HND": [
        {"name": "ANA Mileage Club (via Amex)", "url": "https://www.ana.co.jp/en/us/amc/", "program": "MR", "partner": "ANA Mileage Club", "tip": "Transfer MR → ANA (2–5 days). Book ANA awards at ana.co.jp. No fuel surcharges."},
        {"name": "United MileagePlus (ANA awards)", "url": "https://www.united.com/en/us/fly/mileageplus.html", "tip": "Book ANA-operated flights through United.com with no fuel surcharges."},
        {"name": "Singapore KrisFlyer", "url": "https://www.singaporeair.com/en_UK/us/ppsclub-krisflyer/", "program": "MR", "partner": "Singapore KrisFlyer", "tip": "Good for ANA/JAL awards via Singapore KrisFlyer."},
    ],
    "BKK": [
        {"name": "Singapore KrisFlyer", "url": "https://www.singaporeair.com/en_UK/us/ppsclub-krisflyer/", "program": "MR", "partner": "Singapore KrisFlyer", "tip": "Transfer MR or CAP1 → KrisFlyer. Great SQ awards to Bangkok."},
        {"name": "EVA Air Infinity MileageLands", "url": "https://www.evaair.com/en-global/evaair-infinity-mileagelands/", "tip": "EVA Air is 5-star rated and flies EWR/LAX–BKK directly."},
        {"name": "Turkish Miles&Smiles (via CAP1)", "url": "https://www.turkishairlines.com/en-us/miles-and-smiles/", "program": "CAP1", "partner": "Turkish Miles&Smiles", "tip": "Turkish has excellent Star Alliance coverage to Asia."},
    ],
    "EZE": [
        {"name": "Air France Flying Blue", "url": "https://www.airfranceklm.com/en/flying-blue/", "program": "MR", "partner": "Air France/KLM Flying Blue"},
        {"name": "Avianca LifeMiles (via CAP1)", "url": "https://www.lifemiles.com/", "program": "CAP1", "partner": "Avianca LifeMiles", "tip": "LifeMiles often prices Buenos Aires well on Star Alliance carriers."},
    ],
    "LIM": [
        {"name": "Avianca LifeMiles (via CAP1)", "url": "https://www.lifemiles.com/", "program": "CAP1", "partner": "Avianca LifeMiles", "tip": "Best for Lima — transfer CAP1 → LifeMiles instantly. Book on lifemiles.com."},
        {"name": "Air France Flying Blue", "url": "https://www.airfranceklm.com/en/flying-blue/", "program": "MR", "partner": "Air France/KLM Flying Blue"},
    ],
    "YVR": [
        {"name": "Air Canada Aeroplan (via CAP1)", "url": "https://www.aircanada.com/aeroplan", "program": "CAP1", "partner": "Air Canada Aeroplan", "tip": "Best option — transfer CAP1 → Aeroplan 1:1 (instant). Book on aircanada.com."},
        {"name": "British Airways Avios", "url": "https://www.britishairways.com/en-us/executive-club/spending-avios/on-flights", "program": "MR", "partner": "British Airways Executive Club"},
    ],
    "CUN": [
        {"name": "American Airlines AAdvantage", "url": "https://www.aa.com/aadvantage/landing.do", "tip": "Book on aa.com — AA has the most direct service and frequent awards to Cancún."},
        {"name": "United MileagePlus", "url": "https://www.united.com/en/us/fly/mileageplus.html", "tip": "United also has good coverage. Check united.com for saver awards."},
    ],
    "PUJ": [
        {"name": "JetBlue TrueBlue", "url": "https://trueblue.jetblue.com/", "tip": "JetBlue has direct service and solid award rates to Punta Cana."},
        {"name": "American Airlines AAdvantage", "url": "https://www.aa.com/aadvantage/landing.do"},
    ],
    "NAS": [
        {"name": "American Airlines AAdvantage", "url": "https://www.aa.com/aadvantage/landing.do", "tip": "AA has the most direct service and low award rates to Nassau."},
        {"name": "JetBlue TrueBlue", "url": "https://trueblue.jetblue.com/", "tip": "JetBlue offers direct MRB service from key hubs."},
    ],
    "SJD": [
        {"name": "American Airlines AAdvantage", "url": "https://www.aa.com/aadvantage/landing.do", "tip": "AA has heavy direct service to Los Cabos — check saver award availability."},
        {"name": "Alaska Mileage Plan", "url": "https://www.alaskaair.com/content/mileage-plan", "tip": "Alaska often prices SJD awards competitively."},
    ],
}

# ── Airline booking portals for cash mode ─────────────────────────────────────
AIRLINE_BOOK_URLS: dict[str, str] = {
    "Air France": "https://www.airfrance.us/",
    "British Airways": "https://www.britishairways.com/en-us/",
    "United": "https://www.united.com/",
    "Delta": "https://www.delta.com/",
    "American": "https://www.aa.com/",
    "JetBlue": "https://www.jetblue.com/",
    "Alaska": "https://www.alaskaair.com/",
    "Air Canada": "https://www.aircanada.com/",
    "LATAM": "https://www.latamairlines.com/us/en/",
    "JAL": "https://www.jal.com/en/",
    "ANA": "https://www.ana.co.jp/en/us/",
    "EVA Air": "https://www.evaair.com/en-global/",
    "Thai Airways": "https://www.thaiairways.com/",
    "Icelandair": "https://www.icelandair.com/",
    "ITA Airways": "https://www.itaairways.com/en/",
    "Aegean Airlines": "https://en.aegeanair.com/",
    "Singapore Airlines": "https://www.singaporeair.com/",
}

COMPARE_URLS = [
    "https://www.google.com/flights",
    "https://www.kayak.com/",
]


class PlaybookRequest(BaseModel):
    option_id: str
    points_strategy_override: str | None = None


@router.post('/generate', response_model=PlaybookResponse)
def generate_playbook(req: PlaybookRequest):
    recs = load_recommendations()
    rec = recs.get(req.option_id)
    if not rec:
        raise HTTPException(404, "Option not found. Generate recommendations first.")

    trip = load_trip_searches().get(rec["trip_search_id"])
    if not trip:
        raise HTTPException(404, "Trip search context not found")

    balances = {b.get("program"): int(b.get("balance", 0)) for b in trip["payload"].get("balances", [])}
    search_mode = rec.get("search_mode", "points")
    destination = rec.get("destination", "")
    origin = rec.get("origin", trip["payload"].get("origins", [""])[0])
    airline = rec.get("airline", "")
    city_name = rec.get("city_name", destination)
    depart_date = trip["payload"].get("date_window_start", "")
    return_date = trip["payload"].get("date_window_end", "")
    cabin = trip["payload"].get("cabin_preference", "economy")

    portals = BOOKING_PORTALS.get(destination, [])

    # ── Cash mode: no transfer steps, just find and book ──────────────────────
    if search_mode == "cash":
        airline_url = AIRLINE_BOOK_URLS.get(airline, "")
        transfer_steps = [
            f"No points transfer needed — this is a cash booking.",
            f"Compare final prices on Google Flights: https://www.google.com/flights before booking.",
        ]
        booking_steps = [
            f"Search {origin} → {destination} ({city_name}) departing {depart_date}" +
            (f", returning {return_date}" if return_date else "") + f" for your party.",
        ]
        if airline_url:
            booking_steps.append(f"Book directly with {airline}: {airline_url} (direct fares often cheapest).")
        booking_steps.extend([
            "Cross-check on Google Flights (https://www.google.com/flights) and Kayak (https://www.kayak.com/) before purchasing.",
            "Consider using a travel credit card for this purchase to earn points on cash spend.",
            "Take a screenshot of the final total before checkout.",
        ])
        return PlaybookResponse(
            option_id=req.option_id,
            transfer_steps=transfer_steps,
            booking_steps=booking_steps,
            warnings=["Prices shown are estimated — always verify live pricing before booking."],
            fallbacks=[
                "Try ±1 day on departure/return for lower fares.",
                "Check incognito mode — some sites show higher prices after repeat visits.",
                f"Try alternate origin airports nearby {origin} for better pricing.",
            ],
        )

    # ── Points mode ───────────────────────────────────────────────────────────
    flight_program = rec.get("suggested_flight_program", "MR")
    flight_points_required = int(rec.get("flight_points_required", 0))
    hotel_points_required = int(rec.get("hotel_points_required", 0))
    points_strategy = rec.get("points_strategy", "none")
    alternates = rec.get("points_strategy_alternates", [])
    taxes_fees = float(rec.get("taxes_fees", 0.0))
    cpp_threshold = float(rec.get("cpp_threshold", 1.0))
    cpp_flight = float(rec.get("cpp_flight", 0.0))

    if req.points_strategy_override in ("flight", "hotel", "none"):
        if not alternates or req.points_strategy_override in alternates or req.points_strategy_override == "none":
            points_strategy = req.points_strategy_override

    program_meta = TRANSFER_PARTNERS.get(flight_program, {})
    program_label = program_meta.get("label", flight_program)
    all_partners = program_meta.get("partners", {})

    # Find the best portal for this destination + program combo
    best_portal = next((p for p in portals if p.get("program") == flight_program), None)
    # If no portal matches the exact program, fall back to first portal
    if not best_portal and portals:
        best_portal = portals[0]
    best_partner_name = best_portal.get("partner") if best_portal else None
    best_partner = all_partners.get(best_partner_name, {}) if best_partner_name else {}

    # Cross-reference transfer_partners table: find which programs can reach the
    # destination airline so we can suggest alternatives if the user's card can't.
    airline_programs = get_programs_for_airline(airline) if airline else []
    reachable_from_user: list[str] = []
    for card_col, bk in CARD_TO_BACKEND.items():
        if balances.get(bk, 0) > 0:
            reachable = get_transferable_programs_for_backend(bk)
            reachable_names = {p["program"] for p in reachable}
            for ap in airline_programs:
                if ap["program"] in reachable_names:
                    entry = f"{ap['program']} (via {bk})"
                    if entry not in reachable_from_user:
                        reachable_from_user.append(entry)

    transfer_steps = [
        f"CPP check: estimated {cpp_flight:.1f}¢/pt on this route (threshold: {cpp_threshold:.1f}¢). "
        f"{'Above threshold — use points.' if cpp_flight > cpp_threshold else 'Below threshold — consider cash.'}",
    ]
    if reachable_from_user:
        transfer_steps.append(
            f"Programs that can book {airline or city_name} from your balances: "
            + ", ".join(reachable_from_user[:4])
            + ("." if reachable_from_user else "")
        )
    booking_steps = []
    warnings = [
        "All award prices are estimated. Confirm live availability before transferring points.",
        "Transfers are irreversible — only transfer once you've verified award space.",
        "Award availability can vanish between search and checkout.",
    ]

    if points_strategy == "flight":
        if best_partner_name and best_partner:
            transfer_steps.extend([
                f"Log in to your {program_label} account.",
                f"Transfer {flight_points_required:,} pts → {best_partner_name} ({best_partner['ratio']}, {best_partner['speed']}).",
                f"Transfer portal: {best_partner.get('transfer_url', '')}",
            ])
            booking_steps.append(
                f"Once transfer completes ({best_partner['speed']}), log in to {best_partner_name}."
            )
            if best_portal:
                booking_steps.append(f"Search award: {origin} → {destination}, {cabin} cabin, {depart_date}" +
                                     (f" return {return_date}" if return_date else "") + ".")
                booking_steps.append(f"Booking link: {best_portal['url']}")
                if best_portal.get("tip"):
                    booking_steps.append(f"Tip: {best_portal['tip']}")
        else:
            # Generic fallback if no specific partner mapped
            transfer_steps.extend([
                f"Log in to your {program_label} account.",
                f"Transfer {flight_points_required:,} pts to your preferred airline partner (1:1 ratio).",
                f"Transfer partners: https://www.americanexpress.com/en-us/rewards/membership-rewards/partners/",
            ])

        booking_steps.extend([
            f"Expect ~${taxes_fees:.0f} in taxes/fees at checkout (cash charge on the award booking).",
            "Book hotel separately in cash for this itinerary.",
            "Screenshot the confirmation page showing points used + taxes paid.",
        ])

        available = balances.get(flight_program, 0)
        if available < flight_points_required:
            warnings.append(
                f"Balance check: you have {available:,} {flight_program} pts — "
                f"need {flight_points_required:,}. Gap: {flight_points_required - available:,} pts."
            )

        if best_partner.get("speed", "") not in ("instant", ""):
            warnings.append(
                f"{best_partner_name} transfers take {best_partner.get('speed')} — "
                "don't transfer until you've confirmed award space is available."
            )

    elif points_strategy == "hotel":
        marriott_meta = TRANSFER_PARTNERS.get("MARRIOTT", {})
        transfer_steps.extend([
            "Hotel CPP is stronger than flight CPP for this option — use Marriott Bonvoy points on the hotel.",
            "No transfer needed for Marriott — book directly through the Bonvoy portal.",
        ])
        booking_steps.extend([
            "Book the flight in cash (see comparison sites below).",
            f"Book hotel via Marriott Bonvoy: {marriott_meta.get('book_url', 'https://www.marriott.com/rewards/')}",
            f"Search for properties in {city_name} for your dates.",
            "Filter by 'Use Points' — confirm the property participates in Bonvoy.",
        ])

        marriott_balance = balances.get("MARRIOTT", 0)
        if marriott_balance < hotel_points_required:
            warnings.append(
                f"Balance check: you have {marriott_balance:,} Marriott pts — "
                f"need ~{hotel_points_required:,}."
            )

    else:
        transfer_steps.append(
            f"Neither flight nor hotel clears the {cpp_threshold:.1f}¢ CPP threshold — use cash for both."
        )
        booking_steps.extend([
            "Book flight in cash.",
            "Book hotel in cash.",
            "Hold points for a stronger redemption opportunity (target >1.5¢/pt).",
        ])

    # Add comparison + fallback portal links
    if portals:
        booking_steps.append("── Alternative booking portals for this route ──")
        for p in portals[:3]:
            entry = f"{p['name']}: {p['url']}"
            if p.get("tip"):
                entry += f" — {p['tip']}"
            booking_steps.append(entry)

    booking_steps.append("Compare cash fares: https://www.google.com/flights")
    booking_steps.append("Screenshot your final confirmation before closing the browser.")

    fallbacks = [
        "Try ±1–2 days on departure/return — award space varies day by day.",
        f"Try alternate origin airport near {origin} (same metro area often has award seats on different dates).",
        "If primary partner shows no space, check the other portals listed above.",
    ]

    if balances.get("MR", 0) > 0 and balances.get("CAP1", 0) > 0:
        alt_program = "CAP1" if flight_program == "MR" else "MR"
        alt_label = TRANSFER_PARTNERS.get(alt_program, {}).get("label", alt_program)
        fallbacks.append(f"If {program_label} transfer fails, try {alt_label} partners for this route.")

    # Suggest additional reachable programs from the transfer table
    if len(reachable_from_user) > 1:
        fallbacks.append(
            "Other programs in your wallet that fly this airline: "
            + ", ".join(reachable_from_user[1:4]) + "."
        )

    return PlaybookResponse(
        option_id=req.option_id,
        transfer_steps=transfer_steps,
        booking_steps=booking_steps,
        warnings=warnings,
        fallbacks=fallbacks,
    )
