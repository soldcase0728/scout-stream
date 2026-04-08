'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getSwing, editEvents, updateSwingNotes } from '@/lib/api';
import type { Swing, CheckpointMetrics } from '@/lib/types';

export default function SwingViewerPage() {
  const params = useParams();
  const swingId = params.id as string;
  const [swing, setSwing] = useState<Swing | null>(null);
  const [notes, setNotes] = useState('');
  const [editingEvents, setEditingEvents] = useState(false);
  const [eventFrames, setEventFrames] = useState({ start: 0, launch: 0, contact: 0 });

  useEffect(() => {
    loadSwing();
  }, [swingId]);

  const loadSwing = () => {
    getSwing(swingId).then((res) => {
      setSwing(res.data);
      setNotes(res.data.notes || '');
      if (res.data.events) {
        setEventFrames({
          start: res.data.events.final_start,
          launch: res.data.events.final_launch,
          contact: res.data.events.final_contact,
        });
      }
    });
  };

  const handleSaveEvents = async () => {
    await editEvents(swingId, {
      final_start_frame: eventFrames.start,
      final_launch_frame: eventFrames.launch,
      final_contact_frame: eventFrames.contact,
    });
    setEditingEvents(false);
    loadSwing();
  };

  const handleSaveNotes = async () => {
    await updateSwingNotes(swingId, notes);
  };

  if (!swing) return <p className="text-gray-500">Loading...</p>;

  if (swing.status !== 'review_ready') {
    return (
      <div className="text-center py-16">
        <p className="text-lg font-medium">Processing: {swing.status}</p>
        <p className="text-gray-500 mt-2">Refresh the page to check for updates.</p>
        <button
          onClick={loadSwing}
          className="mt-4 bg-scout-600 text-white px-4 py-2 rounded"
        >
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold">Swing Analysis</h1>
          <p className="text-gray-500 text-sm">{swing.swing_type} swing</p>
        </div>
        {swing.interpretation && (
          <span
            className={`text-sm px-3 py-1 rounded font-medium ${
              swing.interpretation.severity === 'high'
                ? 'bg-red-100 text-red-800'
                : swing.interpretation.severity === 'medium'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-green-100 text-green-800'
            }`}
          >
            {swing.interpretation.severity} priority
          </span>
        )}
      </div>

      {/* Video Player */}
      <div className="bg-black rounded-lg overflow-hidden">
        <video
          src={swing.source_video_url}
          controls
          className="w-full max-h-96 mx-auto"
        />
      </div>

      {/* Event Frames */}
      {swing.events && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-semibold">Event Frames</h2>
            <button
              onClick={() => setEditingEvents(!editingEvents)}
              className="text-sm text-scout-600 hover:underline"
            >
              {editingEvents ? 'Cancel' : 'Adjust Frames'}
            </button>
          </div>
          <div className="grid grid-cols-3 gap-4">
            {(['start', 'launch', 'contact'] as const).map((event) => (
              <div key={event} className="text-center">
                <p className="text-xs text-gray-500 uppercase mb-1">{event}</p>
                {editingEvents ? (
                  <input
                    type="number"
                    value={eventFrames[event]}
                    onChange={(e) =>
                      setEventFrames({ ...eventFrames, [event]: parseInt(e.target.value) || 0 })
                    }
                    className="border rounded px-2 py-1 w-20 text-center"
                  />
                ) : (
                  <p className="text-lg font-mono font-bold">
                    {swing.events?.[`final_${event}` as keyof typeof swing.events]}
                  </p>
                )}
              </div>
            ))}
          </div>
          {editingEvents && (
            <button
              onClick={handleSaveEvents}
              className="mt-4 bg-scout-600 text-white px-4 py-2 rounded text-sm"
            >
              Save & Recompute
            </button>
          )}
          <div className="flex justify-between text-xs text-gray-400 mt-2">
            <span>Confidence: {(swing.events.confidence * 100).toFixed(0)}%</span>
            {swing.events.manual_override && <span>Manually adjusted</span>}
          </div>
        </div>
      )}

      {/* Coaching Interpretation */}
      {swing.interpretation && (
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-scout-600">
          <h2 className="font-semibold mb-3">Coaching Summary</h2>
          <div className="space-y-3">
            <div>
              <p className="text-xs text-gray-500 uppercase">What happened</p>
              <p className="text-gray-800">{swing.interpretation.what_happened}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase">What it means</p>
              <p className="text-gray-800">{swing.interpretation.what_it_means}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold">What to coach next</p>
              <p className="text-gray-900 font-medium">{swing.interpretation.what_to_coach_next}</p>
            </div>
          </div>
        </div>
      )}

      {/* Metrics Table */}
      {swing.metrics && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold mb-4">Checkpoint Metrics</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="py-2 pr-4">Metric</th>
                  <th className="py-2 px-4 text-center">Start</th>
                  <th className="py-2 px-4 text-center">Launch</th>
                  <th className="py-2 px-4 text-center">Contact</th>
                </tr>
              </thead>
              <tbody>
                {metricRows.map((row) => (
                  <tr key={row.key} className="border-b">
                    <td className="py-2 pr-4 text-gray-700">{row.label}</td>
                    <td className="py-2 px-4 text-center font-mono">
                      {formatMetric(swing.metrics!.start, row.key)}
                    </td>
                    <td className="py-2 px-4 text-center font-mono">
                      {formatMetric(swing.metrics!.launch, row.key)}
                    </td>
                    <td className="py-2 px-4 text-center font-mono">
                      {formatMetric(swing.metrics!.contact, row.key)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Timing */}
      {swing.timing && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold mb-3">Timing</h2>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-gray-500">Start to Launch</p>
              <p className="text-lg font-mono">{swing.timing.frames_start_to_launch}f</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Launch to Contact</p>
              <p className="text-lg font-mono">{swing.timing.frames_launch_to_contact}f</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Start to Contact</p>
              <p className="text-lg font-mono">{swing.timing.frames_start_to_contact}f</p>
            </div>
          </div>
        </div>
      )}

      {/* Coach Notes */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="font-semibold mb-3">Coach Notes</h2>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="w-full border rounded px-3 py-2 text-sm"
          rows={3}
          placeholder="Add coaching notes for this swing..."
        />
        <button
          onClick={handleSaveNotes}
          className="mt-2 bg-scout-600 text-white px-4 py-2 rounded text-sm"
        >
          Save Notes
        </button>
      </div>
    </div>
  );
}

const metricRows = [
  { key: 'spine_angle', label: 'Spine Angle' },
  { key: 'spine_angle_side', label: 'Spine Side Bend' },
  { key: 'lead_foot_angle', label: 'Lead Foot Angle' },
  { key: 'rear_foot_angle', label: 'Rear Foot Angle' },
  { key: 'hip_angle', label: 'Hip Angle' },
  { key: 'shoulder_angle', label: 'Shoulder Angle' },
  { key: 'shoulder_tilt', label: 'Shoulder Tilt' },
  { key: 'separation', label: 'Separation' },
] as const;

function formatMetric(
  checkpoint: CheckpointMetrics | undefined,
  key: string
): string {
  if (!checkpoint) return '-';
  const val = (checkpoint as unknown as Record<string, number>)[key];
  if (val === undefined || val === null) return '-';
  return `${val.toFixed(1)}°`;
}
