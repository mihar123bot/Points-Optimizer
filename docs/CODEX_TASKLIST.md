# Codex Build Tasklist (MVP)

## Sprint 1 — Foundation
- [ ] TripSearch + PointsBalance data models
- [ ] Destination candidate generation
- [ ] PartnerGraph ingestion skeleton (MR + Cap1)
- [ ] Scoring engine v1 with transparent outputs

## Sprint 2 — Adapters + Results
- [ ] Award adapter interface + one implementation
- [ ] Cash airfare adapter interface + one implementation
- [ ] Generate recommendations endpoint
- [ ] Winner tiles computation

## Sprint 3 — Hotels + Playbook
- [ ] Hotel adapter interface + one implementation/manual fallback
- [ ] Enforce Marriott hotel threshold CPP >= 1.5
- [ ] Booking playbook endpoint

## Sprint 4 — Alerts
- [ ] Saved search alerts model + endpoints
- [ ] Alert evaluator job
- [ ] Email delivery integration

## Acceptance Criteria
- [ ] >=3 viable options generated for seeded scenario when data available
- [ ] Booking playbook exportable/shareable in <60 seconds UX path
- [ ] Every option shows transparent math + source timestamps
- [ ] Partial provider failure does not crash response
