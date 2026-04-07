export interface Coach {
  id: string;
  email: string;
  name: string;
}

export interface Athlete {
  id: string;
  coach_id: string;
  first_name: string;
  last_name: string;
  handedness: string;
  primary_swing_type: string;
  notes: string | null;
  created_at: string;
}

export interface Session {
  id: string;
  athlete_id: string;
  coach_id: string;
  session_type: string | null;
  notes: string | null;
  created_at: string;
}

export interface SwingEvents {
  auto_start: number;
  auto_launch: number;
  auto_contact: number;
  final_start: number;
  final_launch: number;
  final_contact: number;
  manual_override: boolean;
  confidence: number;
}

export interface CheckpointMetrics {
  spine_angle: number;
  spine_angle_side: number;
  spine_position_x: number;
  spine_position_y: number;
  spine_position_z: number;
  lead_foot_angle: number;
  rear_foot_angle: number;
  hip_angle: number;
  shoulder_angle: number;
  shoulder_tilt: number;
  separation: number;
}

export interface SwingMetrics {
  start: CheckpointMetrics;
  launch: CheckpointMetrics;
  contact: CheckpointMetrics;
}

export interface SwingInterpretation {
  what_happened: string;
  what_it_means: string;
  what_to_coach_next: string;
  rules_triggered: { rule_id: string; name: string; priority: string }[];
  severity: string;
}

export interface Swing {
  id: string;
  session_id: string;
  swing_type: string;
  source_video_url: string;
  processed_data_url: string | null;
  status: string;
  pipeline_version: string;
  notes: string | null;
  events: SwingEvents | null;
  metrics: SwingMetrics | null;
  deltas: Record<string, Record<string, number>> | null;
  timing: Record<string, number> | null;
  interpretation: SwingInterpretation | null;
  confidence: { landmark_confidence: number } | null;
}
