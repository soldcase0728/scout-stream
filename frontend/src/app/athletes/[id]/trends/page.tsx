'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getAthlete, getAthleteTrends } from '@/lib/api';
import type { Athlete } from '@/lib/types';

interface TrendEntry {
  swing_id: string;
  swing_type: string;
  created_at: string;
  metrics_contact: Record<string, number>;
  timing: Record<string, number>;
  severity: string | null;
}

const TRACKED_METRICS = [
  { key: 'spine_angle', label: 'Spine Angle' },
  { key: 'separation', label: 'Separation' },
  { key: 'hip_angle', label: 'Hip Angle' },
  { key: 'shoulder_angle', label: 'Shoulder Angle' },
  { key: 'lead_foot_angle', label: 'Lead Foot' },
];

export default function AthleteTrendsPage() {
  const params = useParams();
  const athleteId = params.id as string;
  const [athlete, setAthlete] = useState<Athlete | null>(null);
  const [trends, setTrends] = useState<TrendEntry[]>([]);

  useEffect(() => {
    getAthlete(athleteId).then((res) => setAthlete(res.data)).catch(() => {});
    getAthleteTrends(athleteId).then((res) => setTrends(res.data.swings)).catch(() => {});
  }, [athleteId]);

  if (!athlete) return <p className="text-gray-500">Loading...</p>;

  return (
    <div>
      <div className="mb-6">
        <a href={`/athletes/${athleteId}`} className="text-scout-600 text-sm hover:underline">
          &larr; Back to {athlete.first_name} {athlete.last_name}
        </a>
        <h1 className="text-2xl font-bold mt-2">Progress Trends</h1>
        <p className="text-gray-500 text-sm">
          Contact metrics across {trends.length} swing{trends.length !== 1 ? 's' : ''}
        </p>
      </div>

      {trends.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No analyzed swings yet. Upload and process swings to see trends.
        </div>
      ) : (
        <>
          {/* Metric trend charts (simple bar visualization) */}
          <div className="space-y-6">
            {TRACKED_METRICS.map((metric) => (
              <MetricTrendCard
                key={metric.key}
                label={metric.label}
                metricKey={metric.key}
                trends={trends}
              />
            ))}
          </div>

          {/* Timing trend */}
          <div className="bg-white rounded-lg shadow p-6 mt-6">
            <h2 className="font-semibold mb-4">Launch to Contact Timing</h2>
            <div className="flex items-end gap-1 h-24">
              {trends.map((t, i) => {
                const val = t.timing?.frames_launch_to_contact ?? 0;
                const maxVal = Math.max(...trends.map((e) => e.timing?.frames_launch_to_contact ?? 0), 1);
                return (
                  <div key={i} className="flex-1 flex flex-col items-center">
                    <div
                      className="w-full bg-scout-500 rounded-t"
                      style={{ height: `${(val / maxVal) * 80}px` }}
                      title={`${val} frames`}
                    />
                    <p className="text-[9px] text-gray-400 mt-1">{val}f</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Severity history */}
          <div className="bg-white rounded-lg shadow p-6 mt-6">
            <h2 className="font-semibold mb-4">Issue Severity History</h2>
            <div className="flex gap-2 flex-wrap">
              {trends.map((t, i) => (
                <a
                  key={i}
                  href={`/swings/${t.swing_id}`}
                  className={`w-8 h-8 rounded flex items-center justify-center text-xs font-bold ${
                    t.severity === 'high'
                      ? 'bg-red-100 text-red-700'
                      : t.severity === 'medium'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-green-100 text-green-700'
                  }`}
                  title={`Swing ${i + 1}: ${t.severity}`}
                >
                  {i + 1}
                </a>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function MetricTrendCard({
  label,
  metricKey,
  trends,
}: {
  label: string;
  metricKey: string;
  trends: TrendEntry[];
}) {
  const values = trends.map((t) => t.metrics_contact?.[metricKey] ?? null);
  const validValues = values.filter((v): v is number => v !== null);
  if (validValues.length === 0) return null;

  const min = Math.min(...validValues);
  const max = Math.max(...validValues);
  const range = max - min || 1;
  const avg = validValues.reduce((a, b) => a + b, 0) / validValues.length;
  const latest = validValues[validValues.length - 1];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-semibold">{label} at Contact</h3>
        <div className="text-right text-sm">
          <span className="text-gray-500">Avg: {avg.toFixed(1)}°</span>
          <span className="ml-3 font-mono font-bold">Latest: {latest.toFixed(1)}°</span>
        </div>
      </div>
      <div className="flex items-end gap-1 h-16">
        {values.map((val, i) => {
          if (val === null) return <div key={i} className="flex-1" />;
          const height = ((val - min) / range) * 50 + 10;
          return (
            <div key={i} className="flex-1 flex flex-col items-center">
              <div
                className="w-full bg-scout-500 rounded-t opacity-70 hover:opacity-100 transition-opacity"
                style={{ height: `${height}px` }}
                title={`${val.toFixed(1)}°`}
              />
            </div>
          );
        })}
      </div>
      <div className="flex justify-between text-[9px] text-gray-400 mt-1">
        <span>Oldest</span>
        <span>Latest</span>
      </div>
    </div>
  );
}
