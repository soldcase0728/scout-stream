'use client';

import { useEffect, useState } from 'react';
import { listAthletes, createAthlete } from '@/lib/api';
import type { Athlete } from '@/lib/types';

export default function AthletesPage() {
  const [athletes, setAthletes] = useState<Athlete[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    handedness: 'right',
    primary_swing_type: 'regular',
  });

  useEffect(() => {
    listAthletes().then((res) => setAthletes(res.data)).catch(() => {});
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await createAthlete(form);
    setAthletes([...athletes, res.data]);
    setShowForm(false);
    setForm({ first_name: '', last_name: '', handedness: 'right', primary_swing_type: 'regular' });
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Athletes</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-scout-600 text-white px-4 py-2 rounded hover:bg-scout-700"
        >
          {showForm ? 'Cancel' : 'Add Athlete'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-lg shadow p-6 mb-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="First name"
              value={form.first_name}
              onChange={(e) => setForm({ ...form, first_name: e.target.value })}
              className="border rounded px-3 py-2"
              required
            />
            <input
              type="text"
              placeholder="Last name"
              value={form.last_name}
              onChange={(e) => setForm({ ...form, last_name: e.target.value })}
              className="border rounded px-3 py-2"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <select
              value={form.handedness}
              onChange={(e) => setForm({ ...form, handedness: e.target.value })}
              className="border rounded px-3 py-2"
            >
              <option value="right">Right-handed</option>
              <option value="left">Left-handed</option>
            </select>
            <select
              value={form.primary_swing_type}
              onChange={(e) => setForm({ ...form, primary_swing_type: e.target.value })}
              className="border rounded px-3 py-2"
            >
              <option value="regular">Regular</option>
              <option value="left_slap">Left Slap</option>
            </select>
          </div>
          <button type="submit" className="bg-scout-600 text-white px-4 py-2 rounded">
            Create Athlete
          </button>
        </form>
      )}

      <div className="bg-white rounded-lg shadow">
        {athletes.length === 0 ? (
          <p className="p-6 text-gray-500 text-center">No athletes yet.</p>
        ) : (
          athletes.map((a) => (
            <a
              key={a.id}
              href={`/athletes/${a.id}`}
              className="block px-4 py-3 border-b hover:bg-gray-50 last:border-b-0"
            >
              <span className="font-medium">
                {a.first_name} {a.last_name}
              </span>
              <span className="text-sm text-gray-500 ml-2">
                {a.handedness} / {a.primary_swing_type}
              </span>
            </a>
          ))
        )}
      </div>
    </div>
  );
}
