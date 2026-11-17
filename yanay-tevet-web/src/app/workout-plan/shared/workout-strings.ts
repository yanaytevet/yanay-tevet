import {MuscleGroup, TrackingType} from '../../../generated-files/api/workout-plan';

export type WorkoutLanguage = 'en' | 'he';

export interface WorkoutStrings {
  appTitle: string;
  plansSubtitle: string;
  newPlan: string;
  planName: string;
  createPlan: string;
  emptyPlansTitle: string;
  emptyPlansText: string;
  loadingPlans: string;
  loadingPlan: string;
  loadingWorkout: string;
  loadingProgress: string;
  planNotFound: string;
  backToPlans: string;
  backToPlan: string;
  languageToggle: string;
  progress: string;
  history: string;
  days: string;
  day: string;
  dayCount: string;
  sharedWith: string;
  everyDay: string;
  everyDayHint: string;
  startWorkout: string;
  freeWorkout: string;
  edit: string;
  doneEditing: string;
  addDay: string;
  dayName: string;
  renameDay: string;
  deleteDay: string;
  deleteDayText: string;
  addExercise: string;
  editExercise: string;
  removeExercise: string;
  removeExerciseText: string;
  moveUp: string;
  moveDown: string;
  share: string;
  shareTitle: string;
  shareSubtitle: string;
  planSettings: string;
  renamePlan: string;
  poolLength: string;
  poolLengthText: string;
  deletePlan: string;
  deletePlanText: string;
  noExercisesYet: string;
  noDaysTitle: string;
  noDaysText: string;
  cancel: string;
  save: string;
  delete: string;
  remove: string;
  add: string;
  sets: string;
  reps: string;
  repsMax: string;
  weightKg: string;
  seconds: string;
  distanceKm: string;
  laps: string;
  time: string;
  restSeconds: string;
  notes: string;
  set: string;
  left: string;
  right: string;
  previous: string;
  addSet: string;
  finishWorkout: string;
  reopenWorkout: string;
  finished: string;
  deleteWorkout: string;
  deleteWorkoutText: string;
  rest: string;
  restDone: string;
  skip: string;
  exerciseLibrary: string;
  searchExercises: string;
  allGroups: string;
  noMatches: string;
  newExercise: string;
  createExercise: string;
  nameEnglish: string;
  nameHebrew: string;
  muscleGroup: string;
  tracks: string;
  perSide: string;
  perSideHint: string;
  custom: string;
  firstTime: string;
  nameRequired: string;
  targets: string;
  progressSubtitle: string;
  emptyProgressTitle: string;
  emptyProgressText: string;
  topWeight: string;
  volume: string;
  maxReps: string;
  totalReps: string;
  longestHold: string;
  distance: string;
  pace: string;
  sessionsLogged: string;
  lastTime: string;
  noHistory: string;
  sinceFirst: string;
  setsDone: string;
  exercisesDone: string;
  open: string;
  extraExercises: string;
  minutesShort: string;
  perKm: string;
  per100m: string;
  muscle: Record<MuscleGroup, string>;
  tracking: Record<TrackingType, string>;
}

export const WORKOUT_STRINGS: Record<WorkoutLanguage, WorkoutStrings> = {
  en: {
    appTitle: 'Workout Plan',
    plansSubtitle: 'Your training plans, logged workouts and progress.',
    newPlan: 'New plan',
    planName: 'Plan name',
    createPlan: 'Create plan',
    emptyPlansTitle: 'Build your first plan',
    emptyPlansText: 'Add day types like Day A and Day B, then the exercises for each.',
    loadingPlans: 'Loading plans',
    loadingPlan: 'Loading plan',
    loadingWorkout: 'Loading workout',
    loadingProgress: 'Loading progress',
    planNotFound: 'This plan could not be loaded.',
    backToPlans: 'All plans',
    backToPlan: 'Back to plan',
    languageToggle: 'עברית',
    progress: 'Progress',
    history: 'History',
    days: 'days',
    day: 'day',
    dayCount: 'Days',
    sharedWith: 'Shared',
    everyDay: 'Every day',
    everyDayHint: 'Done on every training day, before the day\'s own exercises.',
    startWorkout: 'Start',
    freeWorkout: 'Free workout',
    edit: 'Edit plan',
    doneEditing: 'Done',
    addDay: 'Add day',
    dayName: 'Day name',
    renameDay: 'Rename day',
    deleteDay: 'Delete day',
    deleteDayText: 'Delete this day and its exercises? Workouts you already logged are kept.',
    addExercise: 'Add exercise',
    editExercise: 'Edit exercise',
    removeExercise: 'Remove',
    removeExerciseText: 'Remove this exercise from the day? Workouts you already logged are kept.',
    moveUp: 'Move up',
    moveDown: 'Move down',
    share: 'Share',
    shareTitle: 'Share plan',
    shareSubtitle: 'People you add can view and edit the plan. Everyone logs their own workouts.',
    planSettings: 'Plan settings',
    renamePlan: 'Rename plan',
    poolLength: 'Pool length',
    poolLengthText: 'Length of your pool in metres, used to turn laps into distance.',
    deletePlan: 'Delete plan',
    deletePlanText: 'Delete this plan for everyone it is shared with? Logged workouts are kept.',
    noExercisesYet: 'No exercises yet.',
    noDaysTitle: 'Add your first day',
    noDaysText: 'Each day is one kind of workout, such as back and biceps.',
    cancel: 'Cancel',
    save: 'Save',
    delete: 'Delete',
    remove: 'Remove',
    add: 'Add',
    sets: 'Sets',
    reps: 'Reps',
    repsMax: 'max',
    weightKg: 'kg',
    seconds: 'Seconds',
    distanceKm: 'km',
    laps: 'Laps',
    time: 'Time',
    restSeconds: 'Rest (seconds)',
    notes: 'Notes',
    set: 'Set',
    left: 'L',
    right: 'R',
    previous: 'Last time',
    addSet: 'Add set',
    finishWorkout: 'Finish workout',
    reopenWorkout: 'Reopen',
    finished: 'Finished',
    deleteWorkout: 'Delete workout',
    deleteWorkoutText: 'Delete this workout and all its logged sets? This cannot be undone.',
    rest: 'Rest',
    restDone: 'Rest is over',
    skip: 'Skip',
    exerciseLibrary: 'Exercise library',
    searchExercises: 'Search exercises',
    allGroups: 'All',
    noMatches: 'No exercise matches.',
    newExercise: 'New exercise',
    createExercise: 'Create exercise',
    nameEnglish: 'Name (English)',
    nameHebrew: 'Name (Hebrew)',
    muscleGroup: 'Muscle group',
    tracks: 'Tracks',
    perSide: 'Each side separately',
    perSideHint: 'Log the left and right arm or leg on their own.',
    custom: 'Custom',
    firstTime: 'New',
    nameRequired: 'Give the exercise a name.',
    targets: 'Targets',
    progressSubtitle: 'Your own numbers, workout by workout.',
    emptyProgressTitle: 'No workouts logged yet',
    emptyProgressText: 'Start a day from a plan and log your sets — your progress shows up here.',
    topWeight: 'Heaviest set',
    volume: 'Volume',
    maxReps: 'Best set',
    totalReps: 'Total reps',
    longestHold: 'Longest',
    distance: 'Distance',
    pace: 'Pace',
    sessionsLogged: 'workouts',
    lastTime: 'Last',
    noHistory: 'No workouts logged yet.',
    sinceFirst: 'since the first workout',
    setsDone: 'sets',
    exercisesDone: 'exercises',
    open: 'Open',
    extraExercises: 'Added in this workout',
    minutesShort: 'min',
    perKm: '/km',
    per100m: '/100m',
    muscle: {
      chest: 'Chest', back: 'Back', shoulders: 'Shoulders', biceps: 'Biceps', triceps: 'Triceps',
      forearms: 'Forearms', legs: 'Legs', glutes: 'Glutes', calves: 'Calves', abs: 'Abs', cardio: 'Cardio',
      full_body: 'Full body', other: 'Other',
    },
    tracking: {
      reps: 'Reps', weight_reps: 'Weight × reps', time: 'Time', distance: 'Distance', laps: 'Pool laps',
    },
  },
  he: {
    appTitle: 'תוכנית אימונים',
    plansSubtitle: 'תוכניות האימון, האימונים שתיעדת וההתקדמות שלך.',
    newPlan: 'תוכנית חדשה',
    planName: 'שם התוכנית',
    createPlan: 'יצירת תוכנית',
    emptyPlansTitle: 'בנו את התוכנית הראשונה',
    emptyPlansText: 'הוסיפו סוגי ימים כמו יום א׳ ויום ב׳, ואז את התרגילים של כל יום.',
    loadingPlans: 'טוען תוכניות',
    loadingPlan: 'טוען תוכנית',
    loadingWorkout: 'טוען אימון',
    loadingProgress: 'טוען התקדמות',
    planNotFound: 'לא הצלחנו לטעון את התוכנית.',
    backToPlans: 'כל התוכניות',
    backToPlan: 'חזרה לתוכנית',
    languageToggle: 'English',
    progress: 'התקדמות',
    history: 'היסטוריה',
    days: 'ימים',
    day: 'יום',
    dayCount: 'ימים',
    sharedWith: 'משותפת',
    everyDay: 'כל יום',
    everyDayHint: 'נעשה בכל יום אימון, לפני התרגילים של היום.',
    startWorkout: 'התחלה',
    freeWorkout: 'אימון חופשי',
    edit: 'עריכת תוכנית',
    doneEditing: 'סיום',
    addDay: 'הוספת יום',
    dayName: 'שם היום',
    renameDay: 'שינוי שם היום',
    deleteDay: 'מחיקת יום',
    deleteDayText: 'למחוק את היום ואת התרגילים שלו? אימונים שכבר תיעדת יישמרו.',
    addExercise: 'הוספת תרגיל',
    editExercise: 'עריכת תרגיל',
    removeExercise: 'הסרה',
    removeExerciseText: 'להסיר את התרגיל מהיום? אימונים שכבר תיעדת יישמרו.',
    moveUp: 'הזזה למעלה',
    moveDown: 'הזזה למטה',
    share: 'שיתוף',
    shareTitle: 'שיתוף התוכנית',
    shareSubtitle: 'מי שתוסיפו יוכל לראות ולערוך את התוכנית. כל אחד מתעד את האימונים שלו.',
    planSettings: 'הגדרות תוכנית',
    renamePlan: 'שינוי שם התוכנית',
    poolLength: 'אורך הבריכה',
    poolLengthText: 'אורך הבריכה במטרים, כדי להפוך בריכות למרחק.',
    deletePlan: 'מחיקת תוכנית',
    deletePlanText: 'למחוק את התוכנית לכל מי שהיא משותפת איתו? אימונים שתועדו יישמרו.',
    noExercisesYet: 'עוד אין תרגילים.',
    noDaysTitle: 'הוסיפו את היום הראשון',
    noDaysText: 'כל יום הוא סוג אימון, למשל גב ויד קדמית.',
    cancel: 'ביטול',
    save: 'שמירה',
    delete: 'מחיקה',
    remove: 'הסרה',
    add: 'הוספה',
    sets: 'סטים',
    reps: 'חזרות',
    repsMax: 'מקסימום',
    weightKg: 'ק״ג',
    seconds: 'שניות',
    distanceKm: 'ק״מ',
    laps: 'בריכות',
    time: 'זמן',
    restSeconds: 'מנוחה (שניות)',
    notes: 'הערות',
    set: 'סט',
    left: 'שמ׳',
    right: 'ימ׳',
    previous: 'בפעם הקודמת',
    addSet: 'הוספת סט',
    finishWorkout: 'סיום אימון',
    reopenWorkout: 'פתיחה מחדש',
    finished: 'הסתיים',
    deleteWorkout: 'מחיקת אימון',
    deleteWorkoutText: 'למחוק את האימון ואת כל הסטים שתועדו בו? אי אפשר לבטל.',
    rest: 'מנוחה',
    restDone: 'המנוחה נגמרה',
    skip: 'דילוג',
    exerciseLibrary: 'מאגר תרגילים',
    searchExercises: 'חיפוש תרגיל',
    allGroups: 'הכול',
    noMatches: 'אין תרגיל מתאים.',
    newExercise: 'תרגיל חדש',
    createExercise: 'יצירת תרגיל',
    nameEnglish: 'שם (אנגלית)',
    nameHebrew: 'שם (עברית)',
    muscleGroup: 'קבוצת שרירים',
    tracks: 'מה מתעדים',
    perSide: 'כל צד בנפרד',
    perSideHint: 'תיעוד יד או רגל ימין ושמאל בנפרד.',
    custom: 'שלי',
    firstTime: 'חדש',
    nameRequired: 'צריך שם לתרגיל.',
    targets: 'יעדים',
    progressSubtitle: 'המספרים שלך, אימון אחרי אימון.',
    emptyProgressTitle: 'עוד לא תועדו אימונים',
    emptyProgressText: 'התחילו יום מתוך תוכנית ותעדו את הסטים — ההתקדמות תופיע כאן.',
    topWeight: 'הסט הכבד',
    volume: 'נפח',
    maxReps: 'הסט הטוב',
    totalReps: 'סה״כ חזרות',
    longestHold: 'הכי ארוך',
    distance: 'מרחק',
    pace: 'קצב',
    sessionsLogged: 'אימונים',
    lastTime: 'אחרון',
    noHistory: 'עוד לא תועדו אימונים.',
    sinceFirst: 'מאז האימון הראשון',
    setsDone: 'סטים',
    exercisesDone: 'תרגילים',
    open: 'פתיחה',
    extraExercises: 'נוספו באימון הזה',
    minutesShort: 'דק׳',
    perKm: 'לק״מ',
    per100m: 'ל-100 מ׳',
    muscle: {
      chest: 'חזה', back: 'גב', shoulders: 'כתפיים', biceps: 'יד קדמית', triceps: 'יד אחורית',
      forearms: 'אמות', legs: 'רגליים', glutes: 'ישבן', calves: 'שוקיים', abs: 'בטן', cardio: 'אירובי',
      full_body: 'כל הגוף', other: 'אחר',
    },
    tracking: {
      reps: 'חזרות', weight_reps: 'משקל × חזרות', time: 'זמן', distance: 'מרחק', laps: 'בריכות',
    },
  },
};
