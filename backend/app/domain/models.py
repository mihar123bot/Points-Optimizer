from typing import List, Optional, Literal
from pydantic import BaseModel, Field

Cabin = Literal["economy", "premium_economy", "business", "first"]


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
    points_breakdown: dict = Field(default_factory=dict)
    friction_components: dict = Field(default_factory=dict)
    score_components: dict = Field(default_factory=dict)
    marriott_points_eligible: bool = False
    hotel_booking_mode: str = "cash"
    source_timestamps: dict = Field(default_factory=dict)


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
