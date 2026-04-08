'use client';

import { useEffect, useRef } from 'react';

interface LandmarkPoint {
  x: number;
  y: number;
  z: number;
}

interface FrameLandmarks {
  [key: string]: LandmarkPoint;
}

interface Props {
  landmarks: FrameLandmarks;
  width: number;
  height: number;
  label: string;
  color?: string;
}

// Body connections to draw as lines
const SKELETON_CONNECTIONS: [string, string][] = [
  // Trunk line
  ['pelvis_mid', 'shoulder_mid'],
  // Hip line
  ['left_hip', 'right_hip'],
  // Shoulder line
  ['left_shoulder', 'right_shoulder'],
  // Left leg
  ['left_hip', 'left_knee'],
  ['left_knee', 'left_ankle'],
  ['left_ankle', 'left_heel'],
  ['left_heel', 'left_foot_index'],
  // Right leg
  ['right_hip', 'right_knee'],
  ['right_knee', 'right_ankle'],
  ['right_ankle', 'right_heel'],
  ['right_heel', 'right_foot_index'],
  // Arms
  ['left_shoulder', 'left_wrist'],
  ['right_shoulder', 'right_wrist'],
];

// Key lines to highlight with thicker/different color
const KEY_LINES: { points: [string, string]; color: string; label: string }[] = [
  { points: ['pelvis_mid', 'shoulder_mid'], color: '#ef4444', label: 'Trunk' },
  { points: ['left_hip', 'right_hip'], color: '#3b82f6', label: 'Hips' },
  { points: ['left_shoulder', 'right_shoulder'], color: '#22c55e', label: 'Shoulders' },
];

export default function SkeletonOverlay({ landmarks, width, height, label, color = '#ffffff' }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !landmarks) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, width, height);

    // MediaPipe coordinates are normalized 0-1, where x is left-right, y is top-bottom
    const toPixel = (pt: LandmarkPoint): [number, number] => [
      pt.x * width,
      pt.y * height,
    ];

    // Draw skeleton connections (thin, semi-transparent)
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.globalAlpha = 0.4;
    for (const [a, b] of SKELETON_CONNECTIONS) {
      const ptA = landmarks[a];
      const ptB = landmarks[b];
      if (!ptA || !ptB) continue;
      const [x1, y1] = toPixel(ptA);
      const [x2, y2] = toPixel(ptB);
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }

    // Draw key lines (thicker, full opacity)
    ctx.globalAlpha = 1.0;
    for (const line of KEY_LINES) {
      const ptA = landmarks[line.points[0]];
      const ptB = landmarks[line.points[1]];
      if (!ptA || !ptB) continue;
      const [x1, y1] = toPixel(ptA);
      const [x2, y2] = toPixel(ptB);
      ctx.strokeStyle = line.color;
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }

    // Draw joint points
    ctx.globalAlpha = 0.8;
    const jointNames = [
      'left_hip', 'right_hip', 'left_shoulder', 'right_shoulder',
      'left_knee', 'right_knee', 'left_ankle', 'right_ankle',
      'left_wrist', 'right_wrist', 'pelvis_mid', 'shoulder_mid',
    ];
    for (const name of jointNames) {
      const pt = landmarks[name];
      if (!pt) continue;
      const [x, y] = toPixel(pt);
      ctx.fillStyle = name.includes('mid') ? '#fbbf24' : color;
      ctx.beginPath();
      ctx.arc(x, y, name.includes('mid') ? 5 : 3, 0, Math.PI * 2);
      ctx.fill();
    }

    // Draw foot direction arrows
    ctx.globalAlpha = 0.7;
    for (const side of ['left', 'right']) {
      const heel = landmarks[`${side}_heel`];
      const toe = landmarks[`${side}_foot_index`];
      if (!heel || !toe) continue;
      const [hx, hy] = toPixel(heel);
      const [tx, ty] = toPixel(toe);
      ctx.strokeStyle = '#f97316';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(hx, hy);
      ctx.lineTo(tx, ty);
      ctx.stroke();
      // Arrowhead
      const angle = Math.atan2(ty - hy, tx - hx);
      ctx.beginPath();
      ctx.moveTo(tx, ty);
      ctx.lineTo(tx - 8 * Math.cos(angle - 0.4), ty - 8 * Math.sin(angle - 0.4));
      ctx.moveTo(tx, ty);
      ctx.lineTo(tx - 8 * Math.cos(angle + 0.4), ty - 8 * Math.sin(angle + 0.4));
      ctx.stroke();
    }

    // Label
    ctx.globalAlpha = 1.0;
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 14px sans-serif';
    ctx.fillText(label.toUpperCase(), 10, 22);

    // Key line legend
    ctx.font = '10px sans-serif';
    let legendY = height - 10;
    for (const line of KEY_LINES.slice().reverse()) {
      ctx.fillStyle = line.color;
      ctx.fillRect(10, legendY - 8, 12, 3);
      ctx.fillStyle = '#ffffff';
      ctx.fillText(line.label, 26, legendY - 4);
      legendY -= 14;
    }
  }, [landmarks, width, height, label, color]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="absolute inset-0 pointer-events-none"
    />
  );
}
