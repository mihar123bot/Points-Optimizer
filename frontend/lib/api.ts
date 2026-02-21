import { PlaybookResponse, RecommendationBundle, TripSearchPayload } from '@/lib/types';

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

export async function generatePlaybook(optionId: string): Promise<PlaybookResponse> {
  const res = await fetch(`${API_BASE}/v1/playbook/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ option_id: optionId })
  });
  if (!res.ok) throw new Error(`playbook failed: ${res.status}`);
  return res.json();
}
