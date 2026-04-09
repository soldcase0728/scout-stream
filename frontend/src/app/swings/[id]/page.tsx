'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { getSwing, getSwingStatus, getSwingLandmarks, getSwingFrameImages, getSwingDrills, editEvents, updateSwingNotes } from '@/lib/api';
import type { Swing, CheckpointMetrics } from '@/lib/types';
import SkeletonOverlay from '@/components/swings/SkeletonOverlay';

export default function SwingViewerPage() {
  const params = useParams();
  const swingId = params.id as string;
  const [swing, setSwing] = useState<Swing | null>(null);
  const [notes, setNotes] = useState('');
  const [editingEvents, setEditingEvents] = useState(false);
  const [eventFrames, setEventFrames] = useState({ start: 0, launch: 0, contact: 0 });
  const [landmarks, setLandmarks] = useState<Record<string, Record<string, {x:number;y:number;z:number}>> | null>(null);
  const [drills, setDrills] = useState<{name: string; description: string; focus: string; from_rule: string}[]>([]);
  const [frameImages, setFrameImages] = useState<Record<string, {image: string; width: number; height: number; frame_index: number}> | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadSwing = useCallback(() => {
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
      // Load landmarks, frame images, and drills
      if (res.data.status === 'review_ready') {
        getSwingLandmarks(swingId).then((lRes) => setLandmarks(lRes.data)).catch(() => {});
        getSwingFrameImages(swingId).then((fRes) => setFrameImages(fRes.data)).catch(() => {});
        getSwingDrills(swingId).then((dRes) => setDrills(dRes.data.drills || [])).catch(() => {});
      }
    });
  }, [swingId]);

  // Initial load
  useEffect(() => {
    loadSwing();
  }, [loadSwing]);

  // Auto-poll when processing
  useEffect(() => {
    if (!swing) return;
    const isProcessing = swing.status === 'queued' || swing.status === 'processing' || swing.status === 'uploaded';

    if (isProcessing && !pollRef.current) {
      pollRef.current = setInterval(() => {
        getSwingStatus(swingId).then((res) => {
          if (res.data.status === 'review_ready' || res.data.status === 'failed') {
            if (pollRef.current) clearInterval(pollRef.current);
            pollRef.current = null;
            loadSwing();
          }
        });
      }, 3000);
    }

    if (!isProcessing && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }

    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [swing?.status, swingId, loadSwing]);

  const handleSaveEvents = async () => {
    try {
      await editEvents(swingId, {
        final_start_frame: eventFrames.start,
        final_launch_frame: eventFrames.launch,
        final_contact_frame: eventFrames.contact,
      });
      setEditingEvents(false);
      loadSwing();
    } catch (err) {
      alert('Failed to recompute. Events were saved - try refreshing the page.');
      setEditingEvents(false);
      loadSwing();
    }
  };

  const handleSaveNotes = async () => {
    await updateSwingNotes(swingId, notes);
  };

  if (!swing) return <p className="text-gray-500">Loading...</p>;

  if (swing.status !== 'review_ready') {
    const isError = swing.status === 'failed';
    return (
      <div className="text-center py-16">
        {isError ? (
          <>
            <div className="text-red-500 text-4xl mb-4">!</div>
            <p className="text-lg font-medium text-red-700">Processing Failed</p>
            <p className="text-gray-500 mt-2">
              The video could not be processed. Check video quality and try again.
            </p>
          </>
        ) : (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-scout-600 mx-auto mb-4" />
            <p className="text-lg font-medium">
              {swing.status === 'queued' ? 'Queued for processing...' : 'Analyzing swing...'}
            </p>
            <p className="text-gray-500 mt-2">
              Extracting landmarks, detecting events, computing metrics.
            </p>
            <p className="text-xs text-gray-400 mt-4">Auto-refreshing every 3 seconds</p>
          </>
        )}
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
          src={swing.source_video_url.replace(/^\.\//, '/')}
          controls
          className="w-full max-h-96 mx-auto"
        />
      </div>

      {/* Body Position at Checkpoints - Video Frame + Skeleton Overlay */}
      {(frameImages || landmarks) && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold mb-4">Body Position at Checkpoints</h2>
          <p className="text-xs text-gray-500 mb-3">
            <span className="inline-block w-3 h-0.5 bg-red-500 mr-1 align-middle" /> Trunk
            <span className="inline-block w-3 h-0.5 bg-blue-500 ml-3 mr-1 align-middle" /> Hips
            <span className="inline-block w-3 h-0.5 bg-green-500 ml-3 mr-1 align-middle" /> Shoulders
            <span className="inline-block w-3 h-0.5 bg-orange-500 ml-3 mr-1 align-middle" /> Feet
          </p>
          <div className="grid grid-cols-3 gap-4">
            {(['start', 'launch', 'contact'] as const).map((event) => {
              const fi = frameImages?.[event];
              const overlayW = fi?.width || 220;
              const overlayH = fi?.height || 280;
              return (
              <div key={event} className="relative bg-gray-900 rounded overflow-hidden" style={{height: overlayH, width: overlayW}}>
                {fi && (
                  <img
                    src={`data:image/jpeg;base64,${fi.image}`}
                    alt={`${event} frame ${fi.frame_index}`}
                    className="absolute inset-0 w-full h-full object-cover"
                  />
                )}
                {landmarks?.[event] && (
                  <SkeletonOverlay
                    landmarks={landmarks[event]}
                    width={overlayW}
                    height={overlayH}
                    label={`${event} (f${fi?.frame_index ?? '?'})`}
                  />
                )}
              </div>
              );
            })}
          </div>
        </div>
      )}

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
          {/* Drill recommendation from coaching cue */}
          {swing.interpretation.rules_triggered.length > 0 && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-xs text-gray-500 uppercase mb-2">Triggered Rules</p>
              <div className="flex flex-wrap gap-2">
                {swing.interpretation.rules_triggered.map((r) => (
                  <span
                    key={r.rule_id}
                    className={`text-xs px-2 py-1 rounded ${
                      r.priority === 'high'
                        ? 'bg-red-50 text-red-700'
                        : r.priority === 'medium'
                        ? 'bg-yellow-50 text-yellow-700'
                        : 'bg-green-50 text-green-700'
                    }`}
                  >
                    {r.rule_id}: {r.name.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Drill Recommendations */}
      {drills.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold mb-4">Recommended Drills</h2>
          <div className="space-y-4">
            {drills.map((drill, i) => (
              <div key={i} className="border-l-4 border-scout-500 pl-4">
                <div className="flex items-center gap-2">
                  <h3 className="font-medium">{drill.name}</h3>
                  <span className="text-[10px] bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">
                    {drill.from_rule}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{drill.description}</p>
                <p className="text-xs text-gray-400 mt-1">Focus: {drill.focus}</p>
              </div>
            ))}
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
                  <th className="py-2 px-4 text-center text-gray-400">Delta S→C</th>
                </tr>
              </thead>
              <tbody>
                {metricRows.map((row) => {
                  const startVal = getMetricVal(swing.metrics!.start, row.key);
                  const contactVal = getMetricVal(swing.metrics!.contact, row.key);
                  const delta = startVal != null && contactVal != null ? contactVal - startVal : null;
                  return (
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
                      <td className={`py-2 px-4 text-center font-mono text-xs ${
                        delta != null && Math.abs(delta) > 8 ? 'text-red-600 font-bold' : 'text-gray-400'
                      }`}>
                        {delta != null ? `${delta > 0 ? '+' : ''}${delta.toFixed(1)}` : '-'}
                      </td>
                    </tr>
                  );
                })}
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

function getMetricVal(checkpoint: CheckpointMetrics | undefined, key: string): number | null {
  if (!checkpoint) return null;
  const val = (checkpoint as unknown as Record<string, number>)[key];
  return val ?? null;
}

function formatMetric(checkpoint: CheckpointMetrics | undefined, key: string): string {
  const val = getMetricVal(checkpoint, key);
  if (val === null) return '-';
  return `${val.toFixed(1)}°`;
}
