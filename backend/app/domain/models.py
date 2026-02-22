from typing import List, Optional, Literal
from pydantic import BaseModel, Field

Cabin = Literal["economy", "premium_economy", "business", "first"]
DealRating = Literal["EXCELLENT", "GOOD", "FAIR", "POOR"]
ConfidenceTier = Literal["HIGH", "MEDIUM", "LOW"]
TaxConfidence = Literal["HIGH", "MEDIUM", "LOW"]


class CPPRange(BaseModel):
    cpp_mid: float
    cpp_low: float
    cpp_high: float
    tax_confidence: TaxConfidence


class Valuation(BaseModel):
    cpp_mid: float
    cpp_low: float
    cpp_high: float
    deal_rating: DealRating
    confidence: ConfidenceTier
    score: int  # 0–100


class TransferPath(BaseModel):
    currency: str                    # e.g. "MR", "CAP1"
    program: str                     # e.g. "Air Canada Aeroplan"
    ratio: float                     # 1.0 = 1:1
    promo_bonus_percent: float = 0.0
    effective_points: int            # balance * ratio * (1 + promo/100)
    transfer_time_minutes: int       # 0 = instant


class Constraints(BaseModel):
    max_travel_hours: float = 10.0
    max_stops: int = 1
    nonstop_preferred: bool = True


class PointsBalance(BaseModel):
    program: Literal["MR", "CAP1", "MARRIOTT"]
    balance: int


class TripSearchCreate(BaseModel):
    origins: List[str]
    date_window_start: str
    date_window_end: str
    duration_nights: int = 5
    travelers: int = 2
    vibe_tags: List[str] = Field(default_factory=list)
    preferred_destinations: List[str] = Field(default_factory=list)
    cabin_preference: Cabin = "economy"
    constraints: Constraints = Field(default_factory=Constraints)
    balances: List[PointsBalance] = Field(default_factory=list)


class TripSearch(BaseModel):
    id: str
    payload: TripSearchCreate


class RecommendationOption(BaseModel):
    id: str
    destination: str
    oop_total: float
    cpp_flight: Optional[float] = None
    cpp_hotel: Optional[float] = None
    cpp_blended_capped: float
    score_final: float
    rationale: List[str]
    as_of: str
    # Rich display fields
    search_mode: str = "points"       # "points" | "cash"
    origin: str = ""                  # e.g. "IAD"
    city_name: str = ""               # e.g. "Paris"
    country: str = ""                 # e.g. "France"
    airline: str = ""                 # e.g. "Air France"
    duration: str = ""                # e.g. "7h 50m"
    cash_price_pp: float = 0.0        # cash per person
    # Points details
    points_breakdown: dict = Field(default_factory=dict)
    friction_components: dict = Field(default_factory=dict)
    score_components: dict = Field(default_factory=dict)
    marriott_points_eligible: bool = False
    hotel_booking_mode: str = "cash"
    points_strategy: str = "none"
    cpp_threshold: float = 1.0
    cash_flights_mode: str = "ESTIMATED"
    cash_hotels_mode: str = "ESTIMATED"
    award_mode: str = "ESTIMATED"
    award_details: dict = Field(default_factory=dict)
    validation_steps: List[str] = Field(default_factory=list)
    source_timestamps: dict = Field(default_factory=dict)
    source_labels: dict = Field(default_factory=dict)
    api_mode: str = "fallback"
    # PRD v1 additions
    cpp_range: Optional[CPPRange] = None
    valuation: Optional[Valuation] = None
    transfer_paths: List[TransferPath] = Field(default_factory=list)
    no_award_seats: bool = False


class RecommendationBundle(BaseModel):
    trip_search_id: str
    winner_tiles: dict
    options: List[RecommendationOption]


class PlaybookResponse(BaseModel):
    option_id: str
    transfer_steps: List[str]
    booking_steps: List[str]
    warnings: List[str]
    fallbacks: List[str]
