export type TripSearchPayload = {
  origin_airports: string[];
  preferred_destinations?: string[];
  start_date: string;
  end_date: string;
  max_points_budget: number;
  max_travel_hours?: number;
  stops?: number;
  destination_style?: string[];
  travelers?: number;
};

export type RecommendationOption = {
  option_id: string;
  destination_city: string;
  destination_airport: string;
  source_labels?: string[];
  api_mode?: string;
  estimated_points_total?: number;
  score?: number;
};

export type RecommendationBundle = {
  trip_search_id: string;
  options: RecommendationOption[];
};
