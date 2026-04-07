'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getAthlete, createSession, listSessionSwings } from '@/lib/api';
import type { Athlete, Session } from '@/lib/types';

export default function AthleteDetailPage() {
  const params = useParams();
  const athleteId = params.id as string;
  const [athlete, setAthlete] = useState<Athlete | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [showNewSession, setShowNewSession] = useState(false);
  const [sessionNotes, setSessionNotes] = useState('');

  useEffect(() => {
    getAthlete(athleteId).then((res) => setAthlete(res.data)).catch(() => {});
    // Sessions would come from athlete's sessions endpoint
    // For now we'll handle this through session creation
  }, [athleteId]);

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await createSession({
      athlete_id: athleteId,
      session_type: 'practice',
      notes: sessionNotes,
    });
    window.location.href = `/sessions/${res.data.id}`;
  };

  if (!athlete) return <p className="text-gray-500">Loading...</p>;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">
          {athlete.first_name} {athlete.last_name}
        </h1>
        <p className="text-gray-500">
          {athlete.handedness}-handed / {athlete.primary_swing_type}
        </p>
        {athlete.notes && <p className="text-sm text-gray-600 mt-2">{athlete.notes}</p>}
      </div>

      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Sessions</h2>
        <button
          onClick={() => setShowNewSession(!showNewSession)}
          className="bg-scout-600 text-white px-4 py-2 rounded hover:bg-scout-700 text-sm"
        >
          New Session
        </button>
      </div>

      {showNewSession && (
        <form onSubmit={handleCreateSession} className="bg-white rounded-lg shadow p-6 mb-6">
          <textarea
            placeholder="Session notes (optional)"
            value={sessionNotes}
            onChange={(e) => setSessionNotes(e.target.value)}
            className="w-full border rounded px-3 py-2 mb-4"
            rows={2}
          />
          <button type="submit" className="bg-scout-600 text-white px-4 py-2 rounded text-sm">
            Start Session
          </button>
        </form>
      )}

      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        Create a new session to start analyzing swings.
      </div>
    </div>
  );
}
