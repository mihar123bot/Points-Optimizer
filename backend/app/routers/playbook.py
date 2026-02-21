from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.domain.models import PlaybookResponse
from app.store import load_recommendations, load_trip_searches

router = APIRouter()


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
    flight_program = rec.get("suggested_flight_program", "MR")
    flight_points_required = int(rec.get("flight_points_required", 0))
    hotel_points_required = int(rec.get("hotel_points_required", 0))
    points_strategy = rec.get("points_strategy", "none")
    alternates = rec.get("points_strategy_alternates", [])
    if req.points_strategy_override in ("flight", "hotel", "none"):
        if not alternates or req.points_strategy_override in alternates or req.points_strategy_override == "none":
            points_strategy = req.points_strategy_override
    cpp_threshold = float(rec.get("cpp_threshold", 1.0))

    transfer_steps = [
        f"Re-check live award and cash pricing for {rec['destination']} before booking.",
        f"CPP rule in effect: use points only when CPP > {cpp_threshold:.1f}; if both flight and hotel pass, use points on the higher-CPP side.",
    ]

    booking_steps = []
    warnings = [
        "Transfers are irreversible once submitted.",
        "Availability and pricing can move between search and checkout.",
    ]

    if points_strategy == "flight":
        transfer_steps.append(
            f"Transfer {flight_points_required:,} points from {flight_program} to your chosen airline partner (flight has higher CPP)."
        )
        booking_steps.extend([
            "Book flight first using points.",
            f"Expected taxes/fees on flight award: about ${float(rec.get('taxes_fees', 0.0)):.2f}.",
            "Book hotel in cash for this option.",
        ])

        available_flight_points = balances.get(flight_program, 0)
        if available_flight_points < flight_points_required:
            warnings.append(
                f"Insufficient {flight_program} balance ({available_flight_points:,}) for target transfer ({flight_points_required:,})."
            )

    elif points_strategy == "hotel":
        transfer_steps.append(
            f"Use Marriott points for hotel (~{hotel_points_required:,} points). Hotel CPP is stronger than flight CPP for this option."
        )
        booking_steps.extend([
            "Book flight in cash for this option.",
            "Book hotel using Marriott points.",
            f"Estimated fees payable on hotel points booking are included in OOP model.",
        ])

        marriott_balance = balances.get("MARRIOTT", 0)
        if marriott_balance < hotel_points_required:
            warnings.append(
                f"Insufficient Marriott balance ({marriott_balance:,}) for target hotel points ({hotel_points_required:,})."
            )

    else:
        transfer_steps.append("Neither flight nor hotel clears CPP threshold. Use cash for both.")
        booking_steps.extend([
            "Book flight in cash.",
            "Book hotel in cash.",
            "Keep points for a stronger redemption opportunity.",
        ])

    booking_steps.append("Take screenshots of final totals before checkout for tracking.")
    for step in rec.get("validation_steps", []):
        booking_steps.append(f"Validate: {step}")
    source_url = rec.get("award_details", {}).get("source_url")
    if source_url:
        booking_steps.append(f"Validation link: {source_url}")

    fallbacks = [
        "Try ±1 day on departure and return dates.",
        "Try alternate origin airport (IAD/DCA/BWI or another allowed US hub).",
        "If this option weakens, compare top 3 again and re-run playbook.",
    ]

    if balances.get("MR", 0) > 0 and balances.get("CAP1", 0) > 0:
        alt_program = "CAP1" if flight_program == "MR" else "MR"
        fallbacks.append(f"If transfer path fails, test routing with {alt_program} partner inventory.")

    return PlaybookResponse(
        option_id=req.option_id,
        transfer_steps=transfer_steps,
        booking_steps=booking_steps,
        warnings=warnings,
        fallbacks=fallbacks,
    )
