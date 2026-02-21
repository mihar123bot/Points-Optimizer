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
    program: 'MR' | 'CAP1' | 'MARRIOTT';
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
  points_strategy?: string;
  api_mode?: string;
  award_mode?: string;
  cash_flights_mode?: string;
  cash_hotels_mode?: string;
  points_breakdown?: {
    flight_points?: number;
    hotel_points?: number;
  };
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
