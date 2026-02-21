# Architecture (v0.1 MVP)

## High-level
1. User creates a Trip Search (origins, date window, duration, constraints, balances)
2. Destination recommender proposes candidates
3. Flight + hotel adapters fetch options (cash + awards)
4. Scoring engine computes OOP, CPP, friction, and total score
5. API returns winner tiles + ranked options + explainability math
6. User opens an option and gets Booking Playbook steps
7. Alerts monitor saved searches and notify on conditions

## Services
- **API service (FastAPI)**
  - Trip search CRUD
  - Recommendation generation
  - Playbook generation
  - Alert CRUD
- **Workers (scheduled jobs)**
  - Partner graph refresh (daily)
  - Deal layer refresh (provider cadence)
  - Alert evaluation loop
- **Provider adapters**
  - Award availability provider
  - Cash airfare provider
  - Hotel pricing provider

## Core modules
- `domain/models.py`: Pydantic models + enums
- `services/scoring.py`: OOP/CPP/friction and ranking
- `services/recommender.py`: destination candidate logic
- `services/playbook.py`: transfer + booking checklist generation
- `adapters/*`: provider interfaces and implementations

## Caching/freshness
- Cache provider calls by `(origin,destination,date,cabin,pax)` keys
- Return `as_of` timestamps on all priced entities
- Graceful degradation: return partial options when one provider fails

## Compliance guardrails
- No automated booking
- No credential storage/linking in MVP
- No brittle scraping by default

## Recommended infra (later)
- Postgres + Redis + worker queue
- Rate limit + retries + circuit breaker per provider
