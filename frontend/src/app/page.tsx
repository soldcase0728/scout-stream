'use client';

import { useEffect, useState } from 'react';
import { listAthletes } from '@/lib/api';
import type { Athlete } from '@/lib/types';

export default function Dashboard() {
  const [athletes, setAthletes] = useState<Athlete[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listAthletes()
      .then((res) => setAthletes(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-500">Athletes</p>
          <p className="text-3xl font-bold">{athletes.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-500">Quick Actions</p>
          <a href="/athletes" className="text-scout-600 hover:underline text-sm">
            Manage Athletes
          </a>
        </div>
      </div>

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : athletes.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500 mb-4">No athletes yet.</p>
          <a
            href="/athletes"
            className="bg-scout-600 text-white px-4 py-2 rounded hover:bg-scout-700"
          >
            Add Your First Athlete
          </a>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow">
          <h2 className="text-lg font-semibold p-4 border-b">Recent Athletes</h2>
          {athletes.slice(0, 10).map((a) => (
            <a
              key={a.id}
              href={`/athletes/${a.id}`}
              className="block px-4 py-3 border-b hover:bg-gray-50"
            >
              <span className="font-medium">
                {a.first_name} {a.last_name}
              </span>
              <span className="text-sm text-gray-500 ml-2">
                {a.handedness} / {a.primary_swing_type}
              </span>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
