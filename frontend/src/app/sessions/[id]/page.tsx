'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams } from 'next/navigation';
import { getSession, listSessionSwings, uploadSwing } from '@/lib/api';
import type { Session, Swing } from '@/lib/types';

export default function SessionDetailPage() {
  const params = useParams();
  const sessionId = params.id as string;
  const [session, setSession] = useState<Session | null>(null);
  const [swings, setSwings] = useState<Swing[]>([]);
  const [uploading, setUploading] = useState(false);
  const [swingType, setSwingType] = useState('regular');
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    getSession(sessionId).then((res) => setSession(res.data)).catch(() => {});
    loadSwings();
  }, [sessionId]);

  const loadSwings = () => {
    listSessionSwings(sessionId).then((res) => setSwings(res.data)).catch(() => {});
  };

  const handleUpload = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await uploadSwing(sessionId, file, swingType);
      loadSwings();
    } catch {
      alert('Upload failed');
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  const statusColor = (status: string) => {
    switch (status) {
      case 'review_ready': return 'bg-green-100 text-green-800';
      case 'processing': case 'queued': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (!session) return <p className="text-gray-500">Loading...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Session</h1>
      <p className="text-gray-500 text-sm mb-6">
        {new Date(session.created_at).toLocaleDateString()}
        {session.notes && ` - ${session.notes}`}
      </p>

      {/* Upload */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="font-semibold mb-4">Upload Swing Video</h2>
        <div className="flex gap-4 items-end">
          <div>
            <label className="text-sm text-gray-500 block mb-1">Video file</label>
            <input type="file" accept="video/*" ref={fileRef} className="text-sm" />
          </div>
          <div>
            <label className="text-sm text-gray-500 block mb-1">Swing type</label>
            <select
              value={swingType}
              onChange={(e) => setSwingType(e.target.value)}
              className="border rounded px-2 py-1 text-sm"
            >
              <option value="regular">Regular</option>
              <option value="left_slap">Left Slap</option>
            </select>
          </div>
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="bg-scout-600 text-white px-4 py-2 rounded hover:bg-scout-700 text-sm disabled:opacity-50"
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
      </div>

      {/* Swings list */}
      <h2 className="font-semibold mb-4">Swings ({swings.length})</h2>
      <div className="space-y-3">
        {swings.map((swing) => (
          <a
            key={swing.id}
            href={`/swings/${swing.id}`}
            className="block bg-white rounded-lg shadow p-4 hover:bg-gray-50"
          >
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium">{swing.swing_type}</span>
                <span className={`ml-2 text-xs px-2 py-1 rounded ${statusColor(swing.status)}`}>
                  {swing.status}
                </span>
              </div>
              {swing.interpretation && (
                <span
                  className={`text-xs px-2 py-1 rounded ${
                    swing.interpretation.severity === 'high'
                      ? 'bg-red-100 text-red-800'
                      : swing.interpretation.severity === 'medium'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-green-100 text-green-800'
                  }`}
                >
                  {swing.interpretation.severity}
                </span>
              )}
            </div>
            {swing.interpretation && (
              <p className="text-sm text-gray-600 mt-2">{swing.interpretation.what_happened}</p>
            )}
          </a>
        ))}
        {swings.length === 0 && (
          <p className="text-gray-500 text-center py-8">Upload a swing video to get started.</p>
        )}
      </div>
    </div>
  );
}
