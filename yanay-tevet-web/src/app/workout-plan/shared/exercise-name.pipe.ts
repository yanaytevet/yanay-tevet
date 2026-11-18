import {Pipe, PipeTransform} from '@angular/core';
import {ExerciseSchema} from '../../../generated-files/api/workout-plan';
import {Language} from '../../../generated-files/api/users';

// Pure, with the language as an argument, so names re-render when the language changes.
@Pipe({name: 'exerciseName', standalone: true})
export class ExerciseNamePipe implements PipeTransform {
  transform(exercise: ExerciseSchema | null | undefined, language: Language): string {
    if (!exercise) {
      return '';
    }
    return exerciseName(exercise, language);
  }
}

// Built-in exercises carry every site language (name_translations); a user's own exercise has only the
// English and Hebrew names they typed, so other languages fall back to English, then Hebrew.
export function exerciseName(exercise: ExerciseSchema, language: Language): string {
  if (language === 'he') {
    return exercise.name_he || exercise.name_en;
  }
  return exercise.name_translations[language] || exercise.name_en || exercise.name_he;
}
