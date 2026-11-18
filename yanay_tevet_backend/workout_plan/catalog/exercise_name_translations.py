"""Built-in exercise names in the site languages other than English and Hebrew (those are the catalog's own
name_en/name_he). Keyed by catalog_key, then by language code. Plain data, so migrations can import it."""

EXERCISE_NAME_TRANSLATIONS: dict[str, dict[str, str]] = {
    # Back
    'lat_pulldown': {
        'de': 'Latzug', 'es': 'Jalón al pecho', 'fr': 'Tirage vertical', 'ru': 'Тяга верхнего блока',
        'ar': 'سحب علوي', 'ja': 'ラットプルダウン', 'zh-Hans': '高位下拉',
    },
    'seated_cable_row': {
        'de': 'Kabelrudern sitzend', 'es': 'Remo sentado en polea', 'fr': 'Tirage horizontal à la poulie',
        'ru': 'Тяга нижнего блока сидя', 'ar': 'تجديف بالكابل جالسًا', 'ja': 'シーテッドケーブルロー',
        'zh-Hans': '坐姿绳索划船',
    },
    'machine_row': {
        'de': 'Rudern an der Maschine', 'es': 'Remo en máquina', 'fr': 'Tirage horizontal à la machine',
        'ru': 'Горизонтальная тяга в тренажёре', 'ar': 'تجديف على الجهاز', 'ja': 'マシンロー', 'zh-Hans': '器械划船',
    },
    'single_arm_machine_row': {
        'de': 'Einarmiges Rudern an der Maschine', 'es': 'Remo unilateral en máquina',
        'fr': 'Tirage horizontal à un bras à la machine', 'ru': 'Тяга одной рукой в тренажёре',
        'ar': 'تجديف على الجهاز بذراع واحدة', 'ja': 'ワンアームマシンロー', 'zh-Hans': '单臂器械划船',
    },
    'dumbbell_row': {
        'de': 'Einarmiges Kurzhantelrudern', 'es': 'Remo con mancuerna a una mano', 'fr': 'Rowing haltère à un bras',
        'ru': 'Тяга гантели одной рукой', 'ar': 'تجديف بالدمبل بذراع واحدة', 'ja': 'ワンアームダンベルロー',
        'zh-Hans': '单臂哑铃划船',
    },
    'barbell_row': {
        'de': 'Langhantelrudern', 'es': 'Remo con barra', 'fr': 'Rowing barre', 'ru': 'Тяга штанги в наклоне',
        'ar': 'تجديف بالبار', 'ja': 'バーベルロー', 'zh-Hans': '杠铃划船',
    },
    'pull_up': {
        'de': 'Klimmzug', 'es': 'Dominada', 'fr': 'Traction', 'ru': 'Подтягивания',
        'ar': 'عقلة', 'ja': '懸垂', 'zh-Hans': '引体向上',
    },
    'assisted_pull_up': {
        'de': 'Unterstützter Klimmzug (Maschine)', 'es': 'Dominada asistida en máquina',
        'fr': 'Traction assistée à la machine', 'ru': 'Подтягивания в гравитроне', 'ar': 'عقلة بمساعدة الجهاز',
        'ja': 'アシスト懸垂マシン', 'zh-Hans': '器械辅助引体向上',
    },
    'deadlift': {
        'de': 'Kreuzheben', 'es': 'Peso muerto', 'fr': 'Soulevé de terre', 'ru': 'Становая тяга',
        'ar': 'رفعة ميتة', 'ja': 'デッドリフト', 'zh-Hans': '硬拉',
    },
    'back_extension': {
        'de': 'Rückenstrecker', 'es': 'Hiperextensión lumbar', 'fr': 'Extension lombaire', 'ru': 'Гиперэкстензия',
        'ar': 'تمديد الظهر', 'ja': 'バックエクステンション', 'zh-Hans': '山羊挺身',
    },
    # Biceps
    'ez_bar_curl': {
        'de': 'SZ-Curl', 'es': 'Curl con barra Z', 'fr': 'Curl barre EZ', 'ru': 'Подъём EZ-штанги на бицепс',
        'ar': 'ثني الذراعين بالبار Z', 'ja': 'EZバーカール', 'zh-Hans': 'EZ杠弯举',
    },
    'barbell_curl': {
        'de': 'Langhantel-Curl', 'es': 'Curl con barra', 'fr': 'Curl barre', 'ru': 'Подъём штанги на бицепс',
        'ar': 'ثني الذراعين بالبار', 'ja': 'バーベルカール', 'zh-Hans': '杠铃弯举',
    },
    'dumbbell_curl': {
        'de': 'Alternierender Kurzhantel-Curl', 'es': 'Curl alterno con mancuernas', 'fr': 'Curl alterné aux haltères',
        'ru': 'Попеременный подъём гантелей на бицепс', 'ar': 'ثني الذراعين بالدمبل بالتبادل',
        'ja': 'オルタネイトダンベルカール', 'zh-Hans': '交替哑铃弯举',
    },
    'hammer_curl': {
        'de': 'Hammer-Curl', 'es': 'Curl martillo', 'fr': 'Curl marteau', 'ru': 'Молотковые сгибания',
        'ar': 'ثني الذراعين بقبضة المطرقة', 'ja': 'ハンマーカール', 'zh-Hans': '锤式弯举',
    },
    'cable_rope_curl': {
        'de': 'Kabelcurl mit Seil', 'es': 'Curl en polea con cuerda', 'fr': 'Curl à la poulie avec corde',
        'ru': 'Подъём на бицепс с канатом на блоке', 'ar': 'ثني الذراعين بالحبل على الكابل',
        'ja': 'ケーブルロープカール', 'zh-Hans': '绳索弯举（粗绳）',
    },
    'preacher_curl': {
        'de': 'Scott-Curl', 'es': 'Curl en banco Scott', 'fr': 'Curl au pupitre', 'ru': 'Сгибания на скамье Скотта',
        'ar': 'ثني الذراعين على كرسي الواعظ', 'ja': 'プリーチャーカール', 'zh-Hans': '牧师凳弯举',
    },
    # Chest
    'bench_press': {
        'de': 'Bankdrücken mit Langhantel', 'es': 'Press de banca con barra', 'fr': 'Développé couché à la barre',
        'ru': 'Жим штанги лёжа', 'ar': 'ضغط صدر بالبار', 'ja': 'バーベルベンチプレス', 'zh-Hans': '杠铃卧推',
    },
    'incline_bench_press': {
        'de': 'Schrägbankdrücken', 'es': 'Press inclinado', 'fr': 'Développé incliné',
        'ru': 'Жим на наклонной скамье', 'ar': 'ضغط صدر مائل', 'ja': 'インクラインチェストプレス',
        'zh-Hans': '上斜卧推',
    },
    'chest_press_machine': {
        'de': 'Brustpresse', 'es': 'Press de pecho en máquina', 'fr': 'Presse pectoraux',
        'ru': 'Жим от груди в тренажёре', 'ar': 'ضغط صدر على الجهاز', 'ja': 'チェストプレスマシン',
        'zh-Hans': '器械推胸',
    },
    'dumbbell_bench_press': {
        'de': 'Kurzhantel-Bankdrücken', 'es': 'Press de banca con mancuernas', 'fr': 'Développé couché aux haltères',
        'ru': 'Жим гантелей лёжа', 'ar': 'ضغط صدر بالدمبل', 'ja': 'ダンベルベンチプレス', 'zh-Hans': '哑铃卧推',
    },
    'pec_deck': {
        'de': 'Butterfly (Maschine)', 'es': 'Aperturas en máquina (pec deck)', 'fr': 'Butterfly à la machine (pec deck)',
        'ru': 'Сведение рук в тренажёре (баттерфляй)', 'ar': 'فراشة على الجهاز (بيك ديك)',
        'ja': 'ペックデック（マシンフライ）', 'zh-Hans': '蝴蝶机夹胸',
    },
    'dumbbell_fly': {
        'de': 'Kurzhantel-Fliegende', 'es': 'Aperturas con mancuernas', 'fr': 'Écarté couché aux haltères',
        'ru': 'Разводка гантелей лёжа', 'ar': 'تفتيح صدر بالدمبل', 'ja': 'ダンベルフライ', 'zh-Hans': '哑铃飞鸟',
    },
    'cable_crossover': {
        'de': 'Kabelzug-Crossover', 'es': 'Cruce de poleas', 'fr': 'Écarté poulie vis-à-vis',
        'ru': 'Сведение рук в кроссовере', 'ar': 'تفتيح صدر بالكابل (كروس أوفر)', 'ja': 'ケーブルクロスオーバー',
        'zh-Hans': '龙门架夹胸',
    },
    'push_up': {
        'de': 'Liegestütz', 'es': 'Flexiones', 'fr': 'Pompes', 'ru': 'Отжимания',
        'ar': 'تمرين الضغط', 'ja': '腕立て伏せ', 'zh-Hans': '俯卧撑',
    },
    # Triceps
    'dips': {
        'de': 'Dips', 'es': 'Fondos en paralelas', 'fr': 'Dips', 'ru': 'Отжимания на брусьях',
        'ar': 'متوازي', 'ja': 'ディップス', 'zh-Hans': '双杠臂屈伸',
    },
    'bench_dips': {
        'de': 'Bankdips', 'es': 'Fondos en banco', 'fr': 'Dips sur banc', 'ru': 'Обратные отжимания от скамьи',
        'ar': 'متوازي على البنش', 'ja': 'ベンチディップス', 'zh-Hans': '凳上臂屈伸',
    },
    'triceps_bar_pushdown': {
        'de': 'Trizepsdrücken am Kabel (Stange)', 'es': 'Extensión de tríceps en polea (barra)',
        'fr': 'Extension triceps à la poulie (barre)', 'ru': 'Разгибания на трицепс на блоке (рукоять)',
        'ar': 'دفع ترايسبس بالكابل (بار)', 'ja': 'トライセプスプッシュダウン（バー）', 'zh-Hans': '三头肌下压（直杆）',
    },
    'triceps_rope_pushdown': {
        'de': 'Trizepsdrücken am Seil', 'es': 'Extensión de tríceps en polea con cuerda',
        'fr': 'Extension triceps à la poulie avec corde', 'ru': 'Разгибания на трицепс с канатом',
        'ar': 'دفع ترايسبس بالحبل', 'ja': 'ロープトライセプスプッシュダウン', 'zh-Hans': '三头肌下压（粗绳）',
    },
    'skull_crusher': {
        'de': 'Stirndrücken', 'es': 'Press francés', 'fr': 'Barre au front', 'ru': 'Французский жим',
        'ar': 'ضغط فرنسي', 'ja': 'スカルクラッシャー', 'zh-Hans': '仰卧臂屈伸',
    },
    'overhead_triceps_extension': {
        'de': 'Überkopf-Trizepsstrecken', 'es': 'Extensión de tríceps por encima de la cabeza',
        'fr': 'Extension triceps au-dessus de la tête', 'ru': 'Разгибание рук из-за головы',
        'ar': 'تمديد ترايسبس خلف الرأس', 'ja': 'オーバーヘッドトライセプスエクステンション', 'zh-Hans': '颈后臂屈伸',
    },
    # Shoulders
    'lateral_raise': {
        'de': 'Seitheben', 'es': 'Elevaciones laterales', 'fr': 'Élévations latérales',
        'ru': 'Махи гантелями в стороны', 'ar': 'رفرفة جانبية', 'ja': 'サイドレイズ', 'zh-Hans': '侧平举',
    },
    'shoulder_press': {
        'de': 'Kurzhantel-Schulterdrücken', 'es': 'Press de hombros con mancuernas',
        'fr': 'Développé épaules aux haltères', 'ru': 'Жим гантелей над головой', 'ar': 'ضغط أكتاف بالدمبل',
        'ja': 'ダンベルショルダープレス', 'zh-Hans': '哑铃推肩',
    },
    'shoulder_press_machine': {
        'de': 'Schulterpresse', 'es': 'Press de hombros en máquina', 'fr': 'Développé épaules à la machine',
        'ru': 'Жим на плечи в тренажёре', 'ar': 'ضغط أكتاف على الجهاز', 'ja': 'ショルダープレスマシン',
        'zh-Hans': '器械推肩',
    },
    'front_raise': {
        'de': 'Frontheben', 'es': 'Elevaciones frontales', 'fr': 'Élévations frontales',
        'ru': 'Подъём гантелей перед собой', 'ar': 'رفرفة أمامية', 'ja': 'フロントレイズ', 'zh-Hans': '前平举',
    },
    'wall_supported_raise': {
        'de': 'Kurzhantelheben mit Wandstütze', 'es': 'Elevación con mancuernas apoyado en la pared',
        'fr': 'Élévation aux haltères dos au mur', 'ru': 'Подъём гантелей с упором в стену',
        'ar': 'رفع الدمبل مع الاستناد على الحائط', 'ja': '壁にもたれたダンベルレイズ', 'zh-Hans': '靠墙哑铃上举',
    },
    'rear_delt_fly': {
        'de': 'Reverse Fly', 'es': 'Pájaro (deltoides posterior)', 'fr': 'Oiseau (deltoïdes postérieurs)',
        'ru': 'Обратная разводка на задние дельты', 'ar': 'رفرفة خلفية', 'ja': 'リアデルトフライ',
        'zh-Hans': '反向飞鸟',
    },
    'upright_row': {
        'de': 'Aufrechtes Rudern', 'es': 'Remo al mentón', 'fr': 'Rowing menton', 'ru': 'Тяга к подбородку',
        'ar': 'سحب للذقن', 'ja': 'アップライトロー', 'zh-Hans': '直立划船',
    },
    'face_pull': {
        'de': 'Face Pull', 'es': 'Jalón a la cara (face pull)', 'fr': 'Face pull', 'ru': 'Тяга каната к лицу',
        'ar': 'سحب الحبل للوجه', 'ja': 'フェイスプル', 'zh-Hans': '面拉',
    },
    'shrugs': {
        'de': 'Schulterheben', 'es': 'Encogimientos de hombros', 'fr': "Haussements d'épaules", 'ru': 'Шраги',
        'ar': 'رفع الأكتاف (ترابيس)', 'ja': 'シュラッグ', 'zh-Hans': '耸肩',
    },
    # Legs
    'leg_press': {
        'de': 'Beinpresse', 'es': 'Prensa de piernas', 'fr': 'Presse à cuisses', 'ru': 'Жим ногами',
        'ar': 'ضغط الأرجل', 'ja': 'レッグプレス', 'zh-Hans': '腿举',
    },
    'leg_extension': {
        'de': 'Beinstrecker', 'es': 'Extensión de cuádriceps', 'fr': 'Leg extension',
        'ru': 'Разгибание ног в тренажёре', 'ar': 'تمديد الأرجل على الجهاز', 'ja': 'レッグエクステンション',
        'zh-Hans': '坐姿腿屈伸',
    },
    'leg_curl': {
        'de': 'Beinbeuger', 'es': 'Curl femoral', 'fr': 'Leg curl', 'ru': 'Сгибание ног в тренажёре',
        'ar': 'ثني الأرجل على الجهاز', 'ja': 'レッグカール', 'zh-Hans': '腿弯举',
    },
    'smith_squat': {
        'de': 'Kniebeuge an der Multipresse', 'es': 'Sentadilla en máquina Smith', 'fr': 'Squat à la Smith machine',
        'ru': 'Приседания в Смите', 'ar': 'سكوات على جهاز سميث', 'ja': 'スミスマシンスクワット',
        'zh-Hans': '史密斯深蹲',
    },
    'squat': {
        'de': 'Kniebeuge mit Langhantel', 'es': 'Sentadilla con barra', 'fr': 'Squat à la barre',
        'ru': 'Приседания со штангой', 'ar': 'سكوات بالبار', 'ja': 'バーベルスクワット', 'zh-Hans': '杠铃深蹲',
    },
    'goblet_squat': {
        'de': 'Goblet Squat', 'es': 'Sentadilla goblet', 'fr': 'Goblet squat', 'ru': 'Гоблет-приседания',
        'ar': 'سكوات جوبلت', 'ja': 'ゴブレットスクワット', 'zh-Hans': '高脚杯深蹲',
    },
    'romanian_deadlift': {
        'de': 'Rumänisches Kreuzheben (Kurzhanteln)', 'es': 'Peso muerto rumano (mancuernas)',
        'fr': 'Soulevé de terre roumain (haltères)', 'ru': 'Румынская тяга (гантели)',
        'ar': 'رفعة ميتة رومانية (دمبل)', 'ja': 'ルーマニアンデッドリフト（ダンベル）', 'zh-Hans': '罗马尼亚硬拉（哑铃）',
    },
    'lunges': {
        'de': 'Ausfallschritte', 'es': 'Zancadas', 'fr': 'Fentes', 'ru': 'Выпады',
        'ar': 'طعنات (لانجز)', 'ja': 'ランジ', 'zh-Hans': '弓步蹲',
    },
    'bulgarian_split_squat': {
        'de': 'Bulgarische Kniebeuge', 'es': 'Sentadilla búlgara', 'fr': 'Squat bulgare', 'ru': 'Болгарские выпады',
        'ar': 'سكوات بلغاري', 'ja': 'ブルガリアンスクワット', 'zh-Hans': '保加利亚分腿蹲',
    },
    'hip_thrust': {
        'de': 'Hip Thrust', 'es': 'Hip thrust', 'fr': 'Hip thrust', 'ru': 'Ягодичный мост (хип-траст)',
        'ar': 'دفع الورك (هيب ثرست)', 'ja': 'ヒップスラスト', 'zh-Hans': '臀推',
    },
    'calf_raise': {
        'de': 'Wadenheben', 'es': 'Elevación de gemelos', 'fr': 'Élévation des mollets', 'ru': 'Подъём на носки',
        'ar': 'رفع السمانة', 'ja': 'カーフレイズ', 'zh-Hans': '提踵',
    },
    # Abs
    'crunch': {
        'de': 'Crunch', 'es': 'Crunch abdominal', 'fr': 'Crunch', 'ru': 'Скручивания',
        'ar': 'كرانش', 'ja': 'クランチ', 'zh-Hans': '卷腹',
    },
    'ab_mix': {
        'de': 'Verschiedene Bauchübungen', 'es': 'Ejercicios abdominales variados', 'fr': 'Exercices abdominaux variés',
        'ru': 'Разные упражнения на пресс', 'ar': 'تمارين بطن متنوعة', 'ja': '腹筋トレーニング各種',
        'zh-Hans': '综合腹肌训练',
    },
    'plank': {
        'de': 'Plank', 'es': 'Plancha', 'fr': 'Planche', 'ru': 'Планка',
        'ar': 'بلانك', 'ja': 'プランク', 'zh-Hans': '平板支撑',
    },
    'side_plank': {
        'de': 'Seitstütz', 'es': 'Plancha lateral', 'fr': 'Planche latérale', 'ru': 'Боковая планка',
        'ar': 'بلانك جانبي', 'ja': 'サイドプランク', 'zh-Hans': '侧平板支撑',
    },
    'hanging_leg_raise': {
        'de': 'Hängendes Beinheben', 'es': 'Elevación de piernas colgado', 'fr': 'Relevé de jambes suspendu',
        'ru': 'Подъём ног в висе', 'ar': 'رفع الأرجل معلقًا', 'ja': 'ハンギングレッグレイズ', 'zh-Hans': '悬垂举腿',
    },
    'russian_twist': {
        'de': 'Russian Twist', 'es': 'Giro ruso', 'fr': 'Russian twist', 'ru': 'Русские скручивания',
        'ar': 'تويست روسي', 'ja': 'ロシアンツイスト', 'zh-Hans': '俄罗斯转体',
    },
    'bicycle_crunch': {
        'de': 'Fahrrad-Crunch', 'es': 'Crunch bicicleta', 'fr': 'Crunch vélo', 'ru': 'Скручивания «велосипед»',
        'ar': 'كرانش الدراجة', 'ja': 'バイシクルクランチ', 'zh-Hans': '自行车卷腹',
    },
    # Cardio
    'swimming': {
        'de': 'Schwimmen (Bahnen)', 'es': 'Natación (largos)', 'fr': 'Natation (longueurs)',
        'ru': 'Плавание (длины бассейна)', 'ar': 'سباحة (أطوال المسبح)', 'ja': '水泳（往復数）',
        'zh-Hans': '游泳（泳池趟数）',
    },
    'running': {
        'de': 'Laufen', 'es': 'Carrera', 'fr': 'Course à pied', 'ru': 'Бег',
        'ar': 'جري', 'ja': 'ランニング', 'zh-Hans': '跑步',
    },
    'treadmill': {
        'de': 'Laufband', 'es': 'Cinta de correr', 'fr': 'Tapis de course', 'ru': 'Беговая дорожка',
        'ar': 'جهاز المشي', 'ja': 'トレッドミル', 'zh-Hans': '跑步机',
    },
    'rowing_machine': {
        'de': 'Rudergerät', 'es': 'Máquina de remo', 'fr': 'Rameur', 'ru': 'Гребной тренажёр',
        'ar': 'جهاز التجديف', 'ja': 'ローイングマシン', 'zh-Hans': '划船机',
    },
    'stationary_bike': {
        'de': 'Fahrradergometer', 'es': 'Bicicleta estática', 'fr': 'Vélo stationnaire', 'ru': 'Велотренажёр',
        'ar': 'دراجة ثابتة', 'ja': 'エアロバイク', 'zh-Hans': '健身车',
    },
    'stepper': {
        'de': 'Stepper', 'es': 'Stepper', 'fr': 'Stepper', 'ru': 'Степпер',
        'ar': 'ستيبر', 'ja': 'ステッパー', 'zh-Hans': '踏步机',
    },
    'jump_rope': {
        'de': 'Seilspringen', 'es': 'Saltar la cuerda', 'fr': 'Corde à sauter', 'ru': 'Скакалка',
        'ar': 'نط الحبل', 'ja': '縄跳び', 'zh-Hans': '跳绳',
    },
}
