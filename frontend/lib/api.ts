import { RecommendationBundle, TripSearchPayload } from '@/lib/types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export async function createTripSearch(payload: TripSearchPayload): Promise<{ id: string }> {
  const res = await fetch(`${API_BASE}/v1/trip-searches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`trip-searches failed: ${res.status}`);
  return res.json();
}

export async function generateRecommendations(tripSearchId: string): Promise<RecommendationBundle> {
  const res = await fetch(`${API_BASE}/v1/recommendations/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ trip_search_id: tripSearchId })
  });
  if (!res.ok) throw new Error(`recommendations failed: ${res.status}`);
  return res.json();
}
