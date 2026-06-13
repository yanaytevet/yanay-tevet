import {MeasurementType} from '../../generated-files/api/workout-plan';

export const MEASUREMENT_TYPE_ORDER: MeasurementType[] = ['reps', 'time'];

export const MEASUREMENT_TYPE_LABELS: Record<MeasurementType, string> = {
  reps: 'Repetitions',
  time: 'Time',
};
