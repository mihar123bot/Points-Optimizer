export interface Airport {
  code: string;
  name: string;
  city: string;
}

export const AIRPORTS: Airport[] = [
  // DMV
  { code: 'IAD', name: 'Washington Dulles International', city: 'Washington DC' },
  { code: 'DCA', name: 'Ronald Reagan Washington National', city: 'Washington DC' },
  { code: 'BWI', name: 'Baltimore/Washington International', city: 'Baltimore' },
  // Dallas
  { code: 'DFW', name: 'Dallas Fort Worth International', city: 'Dallas' },
  { code: 'DAL', name: 'Dallas Love Field', city: 'Dallas' },
  // NYC
  { code: 'JFK', name: 'John F. Kennedy International', city: 'New York' },
  { code: 'LGA', name: 'LaGuardia', city: 'New York' },
  { code: 'EWR', name: 'Newark Liberty International', city: 'New York' },
  // Houston
  { code: 'IAH', name: 'George Bush Intercontinental', city: 'Houston' },
  { code: 'HOU', name: 'William P. Hobby', city: 'Houston' },
  // International
  { code: 'CUN', name: 'Cancún International', city: 'Cancún' },
  { code: 'PUJ', name: 'Punta Cana International', city: 'Punta Cana' },
  { code: 'NAS', name: 'Lynden Pindling International', city: 'Nassau' },
  { code: 'SJD', name: 'Los Cabos International', city: 'Los Cabos' },
  { code: 'YVR', name: 'Vancouver International', city: 'Vancouver' },
  { code: 'EZE', name: 'Ministro Pistarini International', city: 'Buenos Aires' },
  { code: 'LIM', name: 'Jorge Chávez International', city: 'Lima' },
  { code: 'CDG', name: 'Charles de Gaulle', city: 'Paris' },
  { code: 'FCO', name: 'Leonardo da Vinci–Fiumicino', city: 'Rome' },
  { code: 'LHR', name: 'Heathrow', city: 'London' },
  { code: 'KEF', name: 'Keflavík International', city: 'Reykjavík' },
  { code: 'ATH', name: 'Athens International', city: 'Athens' },
  { code: 'HND', name: 'Tokyo Haneda', city: 'Tokyo' },
  { code: 'BKK', name: 'Suvarnabhumi', city: 'Bangkok' },
];

export interface Program {
  id: string;
  label: string;
  color: string;
  dotClass: string;
}

export const PROGRAMS: Program[] = [
  { id: 'chase',       label: 'Chase UR', color: '#2563eb', dotClass: 'bg-dot-chase' },
  { id: 'amex',        label: 'Amex MR',  color: '#0ea5e9', dotClass: 'bg-dot-amex'  },
  { id: 'capital_one', label: 'Cap One',  color: '#8b5cf6', dotClass: 'bg-dot-cap'   },
  { id: 'delta',       label: 'Delta',    color: '#c2410c', dotClass: 'bg-dot-delta' },
  { id: 'united',      label: 'United',   color: '#1d4ed8', dotClass: 'bg-dot-united'},
];

export type BackendProgram = 'MR' | 'CAP1';

export const PROGRAM_BACKEND: Record<string, BackendProgram> = {
  chase:       'MR',
  amex:        'MR',
  capital_one: 'CAP1',
  delta:       'MR',
  united:      'MR',
};
