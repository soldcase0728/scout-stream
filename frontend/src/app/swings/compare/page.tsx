'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { compareSwings } from '@/lib/api';
import type { Swing, CheckpointMetrics } from '@/lib/types';

export default function ComparisonPage() {
  return (
    <Suspense fallback={<p className="text-gray-500">Loading...</p>}>
      <ComparisonContent />
    </Suspense>
  );
}

function ComparisonContent() {
  const searchParams = useSearchParams();
  const swingA = searchParams.get('a');
  const swingB = searchParams.get('b');
  const [data, setData] = useState<{ swing_a: Swing; swing_b: Swing } | null>(null);

  useEffect(() => {
    if (swingA && swingB) {
      compareSwings(swingA, swingB).then((res) => setData(res.data)).catch(() => {});
    }
  }, [swingA, swingB]);

  if (!swingA || !swingB) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-500">
          Use URL params ?a=swingId&b=swingId to compare two swings.
        </p>
      </div>
    );
  }

  if (!data) return <p className="text-gray-500">Loading comparison...</p>;

  const metrics = [
    'spine_angle', 'spine_angle_side', 'lead_foot_angle', 'rear_foot_angle',
    'hip_angle', 'shoulder_angle', 'shoulder_tilt', 'separation',
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Swing Comparison</h1>

      {/* Interpretations side by side */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {[data.swing_a, data.swing_b].map((s, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold mb-2">Swing {i === 0 ? 'A' : 'B'}</h3>
            {s.interpretation ? (
              <div className="text-sm space-y-2">
                <p>{s.interpretation.what_happened}</p>
                <p className="font-medium">{s.interpretation.what_to_coach_next}</p>
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No analysis available</p>
            )}
          </div>
        ))}
      </div>

      {/* Metrics comparison table */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="font-semibold mb-4">Metrics at Contact</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-gray-500">
              <th className="py-2 text-left">Metric</th>
              <th className="py-2 text-center">Swing A</th>
              <th className="py-2 text-center">Swing B</th>
              <th className="py-2 text-center">Diff</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((key) => {
              const valA = data.swing_a.metrics?.contact
                ? (data.swing_a.metrics.contact as unknown as Record<string, number>)[key]
                : null;
              const valB = data.swing_b.metrics?.contact
                ? (data.swing_b.metrics.contact as unknown as Record<string, number>)[key]
                : null;
              const diff = valA != null && valB != null ? valB - valA : null;
              return (
                <tr key={key} className="border-b">
                  <td className="py-2">{key.replace(/_/g, ' ')}</td>
                  <td className="py-2 text-center font-mono">
                    {valA != null ? `${valA.toFixed(1)}` : '-'}
                  </td>
                  <td className="py-2 text-center font-mono">
                    {valB != null ? `${valB.toFixed(1)}` : '-'}
                  </td>
                  <td
                    className={`py-2 text-center font-mono ${
                      diff && Math.abs(diff) > 5 ? 'text-red-600 font-bold' : ''
                    }`}
                  >
                    {diff != null ? `${diff > 0 ? '+' : ''}${diff.toFixed(1)}` : '-'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
