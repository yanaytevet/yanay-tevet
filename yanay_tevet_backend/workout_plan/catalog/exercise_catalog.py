"""The built-in exercise library, as plain data so migrations can seed it without importing models.

Each entry: (catalog_key, English name, Hebrew name, muscle group, tracking type, per side).
Keys are permanent: a renamed exercise keeps its key so plans and logs keep pointing at it.
"""

EXERCISE_CATALOG: list[tuple[str, str, str, str, str, bool]] = [
    # Back
    ('lat_pulldown', 'Lat pulldown', 'פולי עליון', 'back', 'weight_reps', False),
    ('seated_cable_row', 'Seated cable row', 'חתירה בכבל בישיבה', 'back', 'weight_reps', False),
    ('machine_row', 'Machine row', 'חתירה במכונה', 'back', 'weight_reps', False),
    ('single_arm_machine_row', 'Single-arm machine row', 'חתירה במכונה יד יד', 'back', 'weight_reps', True),
    ('dumbbell_row', 'Single-arm dumbbell row', 'חתירה עם משקולת יד יד', 'back', 'weight_reps', True),
    ('barbell_row', 'Barbell row', 'חתירה עם מוט', 'back', 'weight_reps', False),
    ('pull_up', 'Pull-up', 'מתח', 'back', 'reps', False),
    ('assisted_pull_up', 'Assisted pull-up machine', 'מתח בעזרת מכונה', 'back', 'weight_reps', False),
    ('deadlift', 'Deadlift', 'דדליפט', 'back', 'weight_reps', False),
    ('back_extension', 'Back extension', 'פשיטת גב', 'back', 'reps', False),
    # Biceps
    ('ez_bar_curl', 'EZ-bar curl', 'כפיפת מרפקים עם מוט W', 'biceps', 'weight_reps', False),
    ('barbell_curl', 'Barbell curl', 'כפיפת מרפקים עם מוט ישר', 'biceps', 'weight_reps', False),
    ('dumbbell_curl', 'Alternating dumbbell curl', 'כפיפת מרפקים עם משקולות יד יד', 'biceps', 'weight_reps', True),
    ('hammer_curl', 'Hammer curl', 'כפיפת פטישים', 'biceps', 'weight_reps', False),
    ('cable_rope_curl', 'Cable rope curl', 'כפיפת מרפקים בחבל', 'biceps', 'weight_reps', False),
    ('preacher_curl', 'Preacher curl', 'כפיפת מרפקים בכיסא כומר', 'biceps', 'weight_reps', False),
    # Chest
    ('bench_press', 'Barbell bench press', 'לחיצת חזה עם מוט', 'chest', 'weight_reps', False),
    ('incline_bench_press', 'Incline chest press', 'לחיצת חזה עליון', 'chest', 'weight_reps', False),
    ('chest_press_machine', 'Chest press machine', 'לחיצת חזה במכונה', 'chest', 'weight_reps', False),
    ('dumbbell_bench_press', 'Dumbbell bench press', 'לחיצת חזה עם משקולות', 'chest', 'weight_reps', False),
    ('pec_deck', 'Pec deck (machine fly)', 'פרפר במכונה', 'chest', 'weight_reps', False),
    ('dumbbell_fly', 'Dumbbell fly', 'פרפר עם משקולות', 'chest', 'weight_reps', False),
    ('cable_crossover', 'Cable crossover', 'פרפר בכבלים', 'chest', 'weight_reps', False),
    ('push_up', 'Push-up', 'שכיבות סמיכה', 'chest', 'reps', False),
    # Triceps
    ('dips', 'Dips', 'מקבילים', 'triceps', 'reps', False),
    ('bench_dips', 'Bench dips', 'מקבילים על ספסל', 'triceps', 'reps', False),
    ('triceps_bar_pushdown', 'Triceps pushdown (bar)', 'פשיטת מרפקים בפולי עם מוט', 'triceps', 'weight_reps', False),
    ('triceps_rope_pushdown', 'Triceps rope pushdown', 'פשיטת מרפקים בחבל', 'triceps', 'weight_reps', False),
    ('skull_crusher', 'Skull crusher', 'לחיצה צרפתית', 'triceps', 'weight_reps', False),
    ('overhead_triceps_extension', 'Overhead triceps extension', 'פשיטת מרפקים מעל הראש', 'triceps', 'weight_reps', False),
    # Shoulders
    ('lateral_raise', 'Lateral raise', 'הרחקת כתפיים', 'shoulders', 'weight_reps', False),
    ('shoulder_press', 'Dumbbell shoulder press', 'לחיצת כתפיים', 'shoulders', 'weight_reps', False),
    ('shoulder_press_machine', 'Shoulder press machine', 'לחיצת כתפיים במכונה', 'shoulders', 'weight_reps', False),
    ('front_raise', 'Front raise', 'הרמה קדמית', 'shoulders', 'weight_reps', False),
    ('wall_supported_raise', 'Wall-supported dumbbell raise', 'הרמת משקולות בהשענות על הקיר', 'shoulders', 'weight_reps', False),
    ('rear_delt_fly', 'Rear delt fly', 'פרפר הפוך', 'shoulders', 'weight_reps', False),
    ('upright_row', 'Upright row', 'חתירה אנכית', 'shoulders', 'weight_reps', False),
    ('face_pull', 'Face pull', 'משיכת פנים בחבל', 'shoulders', 'weight_reps', False),
    ('shrugs', 'Shrugs', 'הרמת כתפיים', 'shoulders', 'weight_reps', False),
    # Legs
    ('leg_press', 'Leg press', 'לחיצת רגליים', 'legs', 'weight_reps', False),
    ('leg_extension', 'Leg extension', 'פשיטת ברכיים במכונה', 'legs', 'weight_reps', False),
    ('leg_curl', 'Leg curl', 'כפיפת ברכיים במכונה', 'legs', 'weight_reps', False),
    ('smith_squat', 'Smith machine squat', 'סקוואט בסמית', 'legs', 'weight_reps', False),
    ('squat', 'Barbell squat', 'סקוואט עם מוט', 'legs', 'weight_reps', False),
    ('goblet_squat', 'Goblet squat', 'סקוואט גביע', 'legs', 'weight_reps', False),
    ('romanian_deadlift', 'Romanian deadlift (dumbbells)', 'דדליפט רומני עם משקולות', 'legs', 'weight_reps', False),
    ('lunges', 'Lunges', 'מכרעים', 'legs', 'weight_reps', True),
    ('bulgarian_split_squat', 'Bulgarian split squat', 'סקוואט בולגרי', 'legs', 'weight_reps', True),
    ('hip_thrust', 'Hip thrust', 'דחיקת אגן', 'glutes', 'weight_reps', False),
    ('calf_raise', 'Calf raise', 'הרמת עקבים', 'calves', 'weight_reps', False),
    # Abs
    ('crunch', 'Crunch', 'כפיפות בטן', 'abs', 'reps', False),
    ('ab_mix', 'Mixed ab exercises', 'תרגילי בטן שונים', 'abs', 'reps', False),
    ('plank', 'Plank', 'פלאנק (בטן סטטית)', 'abs', 'time', False),
    ('side_plank', 'Side plank', 'פלאנק צידי', 'abs', 'time', True),
    ('hanging_leg_raise', 'Hanging leg raise', 'הרמת רגליים בתלייה', 'abs', 'reps', False),
    ('russian_twist', 'Russian twist', 'טוויסט רוסי', 'abs', 'reps', False),
    ('bicycle_crunch', 'Bicycle crunch', 'בטן אופניים', 'abs', 'reps', False),
    # Cardio
    ('swimming', 'Swimming (pool laps)', 'שחייה (בריכות)', 'cardio', 'laps', False),
    ('running', 'Running', 'ריצה', 'cardio', 'distance', False),
    ('treadmill', 'Treadmill', 'הליכון', 'cardio', 'distance', False),
    ('rowing_machine', 'Rowing machine', 'מכונת חתירה', 'cardio', 'distance', False),
    ('stationary_bike', 'Stationary bike', 'אופני כושר', 'cardio', 'time', False),
    ('stepper', 'Stepper', 'סטפר', 'cardio', 'time', False),
    ('jump_rope', 'Jump rope', 'קפיצה בחבל', 'cardio', 'time', False),
]
