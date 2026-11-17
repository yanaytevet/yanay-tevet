import {Pipe, PipeTransform} from '@angular/core';
import {ExerciseSchema} from '../../../generated-files/api/workout-plan';
import {WorkoutLanguage} from './workout-strings';

// Pure, with the language as an argument, so names re-render when the language changes.
@Pipe({name: 'exerciseName', standalone: true})
export class ExerciseNamePipe implements PipeTransform {
  transform(exercise: ExerciseSchema | null | undefined, language: WorkoutLanguage): string {
    if (!exercise) {
      return '';
    }
    return exerciseName(exercise, language);
  }
}

export function exerciseName(exercise: ExerciseSchema, language: WorkoutLanguage): string {
  const preferred = language === 'he' ? exercise.name_he : exercise.name_en;
  const fallback = language === 'he' ? exercise.name_en : exercise.name_he;
  return preferred || fallback;
}
