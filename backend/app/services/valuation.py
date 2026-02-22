"""
Valuation service — pure functions, no I/O.
Computes CPP range, deal rating, and confidence score per PRD v1 §7.
"""
from __future__ import annotations

import time
from app.domain.models import CPPRange, Valuation, DealRating, ConfidenceTier, TaxConfidence

# ── Tax confidence spread (§7.1) ──────────────────────────────────────────────
# Determines how wide the CPP band is based on how well we know the taxes.
TAX_SPREAD: dict[TaxConfidence, float] = {
    "HIGH":   0.08,   # ±8% — taxes from live seats.aero with actual amounts
    "MEDIUM": 0.18,   # ±18% — taxes from Amadeus (approximate)
    "LOW":    0.30,   # ±30% — taxes are estimated
}


def _infer_tax_confidence(source: str, taxes_fees: float) -> TaxConfidence:
    if source == "seats_aero_live" and taxes_fees > 0:
        return "HIGH"
    if source == "amadeus_test" and taxes_fees > 0:
        return "MEDIUM"
    return "LOW"


def compute_cpp_range(
    cash_price: float,
    points_cost: int,
    taxes_fees: float,
    source: str,
) -> CPPRange:
    """
    Compute cpp_mid / cpp_low / cpp_high per PRD §7.1.

    cpp = (cash_price - taxes) / points * 100
    cpp_low  → pessimistic: taxes underestimated → higher real taxes → less value
    cpp_high → optimistic: taxes overestimated → lower real taxes → more value
    """
    tax_conf = _infer_tax_confidence(source, taxes_fees)
    spread = TAX_SPREAD[tax_conf]
    pts = max(points_cost, 1)

    taxes_high_est = taxes_fees * (1 + spread)
    taxes_low_est  = taxes_fees * (1 - spread)

    cpp_mid  = max(0.0, (cash_price - taxes_fees)      / pts * 100)
    cpp_low  = max(0.0, (cash_price - taxes_high_est)  / pts * 100)
    cpp_high = max(0.0, (cash_price - taxes_low_est)   / pts * 100)

    return CPPRange(
        cpp_mid=round(cpp_mid, 2),
        cpp_low=round(cpp_low, 2),
        cpp_high=round(cpp_high, 2),
        tax_confidence=tax_conf,
    )


def rate_deal(cpp_mid: float) -> DealRating:
    """Deal rating thresholds per PRD §7.2."""
    if cpp_mid >= 3.0:
        return "EXCELLENT"
    if cpp_mid >= 2.0:
        return "GOOD"
    if cpp_mid >= 1.3:
        return "FAIR"
    return "POOR"


def compute_confidence(
    last_seen_seconds_ago: float,
    exact_flight_match: bool,
    tax_confidence: TaxConfidence,
    award_source: str,
) -> tuple[int, ConfidenceTier]:
    """
    Confidence score 0–100 per PRD §7.3.

    +30  last_seen < 2h (fresh live availability)
    +30  exact flight match (carrier + flight number)
    +20  taxes HIGH confidence
    +20  source is seats_aero_live
    """
    score = 0
    if last_seen_seconds_ago < 7200:
        score += 30
    if exact_flight_match:
        score += 30
    if tax_confidence == "HIGH":
        score += 20
    elif tax_confidence == "MEDIUM":
        score += 10
    if award_source == "seats_aero_live":
        score += 20

    score = min(100, max(0, score))

    if score >= 80:
        tier: ConfidenceTier = "HIGH"
    elif score >= 50:
        tier = "MEDIUM"
    else:
        tier = "LOW"

    return score, tier


def build_valuation(
    cpp_range: CPPRange,
    confidence_score: int,
    confidence_tier: ConfidenceTier,
) -> Valuation:
    return Valuation(
        cpp_mid=cpp_range.cpp_mid,
        cpp_low=cpp_range.cpp_low,
        cpp_high=cpp_range.cpp_high,
        deal_rating=rate_deal(cpp_range.cpp_mid),
        confidence=confidence_tier,
        score=confidence_score,
    )
