// PRD v1 valuation types
export type DealRating = 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR';
export type ConfidenceTier = 'HIGH' | 'MEDIUM' | 'LOW';

export type Valuation = {
  cpp_mid: number;
  cpp_low: number;
  cpp_high: number;
  deal_rating: DealRating;
  confidence: ConfidenceTier;
  score: number;
};

export type TransferPath = {
  currency: string;
  program: string;
  ratio: number;
  promo_bonus_percent: number;
  effective_points: number;
  transfer_time_minutes: number;
};

export type TripSearchPayload = {
  origins: string[];
  preferred_destinations?: string[];
  date_window_start: string;
  date_window_end: string;
  duration_nights: number;
  travelers: number;
  vibe_tags: string[];
  cabin_preference: 'economy' | 'premium_economy' | 'business' | 'first';
  constraints: {
    max_travel_hours: number;
    max_stops: number;
    nonstop_preferred: boolean;
  };
  balances: Array<{
    program: 'MR' | 'CAP1';
    balance: number;
  }>;
};

export type RecommendationOption = {
  id: string;
  destination: string;
  oop_total: number;
  cpp_flight?: number;
  cpp_hotel?: number;
  cpp_blended_capped: number;
  score_final: number;
  rationale: string[];
  as_of: string;
  // Rich display fields
  search_mode?: string;      // "points" | "cash"
  origin?: string;           // e.g. "IAD"
  city_name?: string;        // e.g. "Paris"
  country?: string;          // e.g. "France"
  airline?: string;          // e.g. "Air France"
  duration?: string;         // e.g. "7h 50m"
  depart_date?: string;      // optimal departure e.g. "2026-07-03"
  return_date?: string;      // optimal return e.g. "2026-07-07"
  cash_price_pp?: number;    // cash price per person
  // Points details
  points_strategy?: string;
  api_mode?: string;
  award_mode?: string;
  cash_flights_mode?: string;
  cash_hotels_mode?: string;
  award_details?: {
    points?: number;
    taxes_fees?: number;
    program?: string;
    cabin?: string;
  };
  points_breakdown?: {
    flight_points?: number;
    hotel_points?: number;
    taxes_fees?: number;
    flight_cpp?: number;
    flight_program?: string;
  };
  // PRD v1 additions
  valuation?: Valuation;
  transfer_paths?: TransferPath[];
  no_award_seats?: boolean;
};

export type RecommendationBundle = {
  trip_search_id: string;
  winner_tiles?: Record<string, string>;
  options: RecommendationOption[];
};

export type PlaybookResponse = {
  option_id: string;
  transfer_steps: string[];
  booking_steps: string[];
  warnings: string[];
  fallbacks: string[];
};
