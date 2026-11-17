import {PlanExerciseSchema} from '../../../generated-files/api/workout-plan';
import {WorkoutStrings} from './workout-strings';

export function formatDuration(totalSeconds: number | null | undefined): string {
  if (totalSeconds === null || totalSeconds === undefined) {
    return '';
  }
  const seconds = Math.max(0, Math.round(totalSeconds));
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const rest = seconds % 60;
  const mmss = `${hours > 0 ? String(minutes).padStart(2, '0') : minutes}:${String(rest).padStart(2, '0')}`;
  return hours > 0 ? `${hours}:${mmss}` : mmss;
}

// "1:30" or "90" → 90. Returns null when the text is not a time.
export function parseDuration(text: string): number | null {
  const trimmed = text.trim();
  if (!trimmed) {
    return null;
  }
  const parts = trimmed.split(':').map(part => Number(part));
  if (parts.some(part => Number.isNaN(part) || part < 0)) {
    return null;
  }
  return parts.reduce((total, part) => total * 60 + part, 0);
}

export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return '';
  }
  return String(Math.round(value * 100) / 100);
}

// One line that says what a plan entry asks for, in the plan's own terms: "4 × 12 · 40 kg".
export function targetSummary(entry: PlanExerciseSchema, t: WorkoutStrings): string {
  const parts: string[] = [];
  switch (entry.exercise.tracking_type) {
    case 'weight_reps':
    case 'reps':
      parts.push(`${entry.target_sets} × ${entry.target_reps ?? t.repsMax}`);
      if (entry.target_weight_kg !== null) {
        parts.push(`${formatNumber(entry.target_weight_kg)} ${t.weightKg}`);
      }
      break;
    case 'time':
      parts.push(`${entry.target_sets} × ${entry.target_seconds !== null ? formatDuration(entry.target_seconds) : t.repsMax}`);
      break;
    case 'distance':
      if (entry.target_distance_km !== null) {
        parts.push(`${formatNumber(entry.target_distance_km)} ${t.distanceKm}`);
      }
      break;
    case 'laps':
      if (entry.target_laps !== null) {
        parts.push(`${entry.target_laps} ${t.laps}`);
      }
      break;
  }
  return parts.join(' · ');
}
