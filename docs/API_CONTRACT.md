# API Contract (MVP)

## Health
- `GET /health` -> `{ status: "ok" }`

## Trip Search
- `POST /v1/trip-searches`
- `GET /v1/trip-searches/{id}`

## Recommendations
- `POST /v1/recommendations/generate`
  - input: `trip_search_id`
  - output:
    - `winner_tiles`: best_oop, best_cpp, best_business, best_balanced
    - `options[]`: includes OOP, points by currency, CPP metrics, friction, rationale, freshness

## Booking Playbook
- `POST /v1/playbook/generate`
  - input: `option_id`
  - output:
    - transfer steps
    - booking checklist
    - warnings + fallback options

## Alerts
- `POST /v1/alerts`
- `GET /v1/alerts?trip_search_id=...`
- `PATCH /v1/alerts/{id}`

## Explainability fields per option
- `oop_total`
- `cpp_flight`
- `cpp_hotel`
- `cpp_blended_capped`
- `friction_components`
- `score_weights`
- `score_final`
