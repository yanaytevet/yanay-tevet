import {JapaneseStrings} from './en';

export const ar: JapaneseStrings = {
  title: 'اليابانية',
  subtitle: 'استكشف شبكة من النصوص والجمل والكلمات وحروف الكانجي والأدوات وقواعد النحو.',
  nav: {
    explore: 'استكشاف',
    ingest: 'إدخال',
    review: 'مراجعة',
  },
  tabs: {
    passage: 'النصوص',
    sentence: 'الجمل',
    word: 'الكلمات',
    kanji: 'الكانجي',
    particle: 'الأدوات',
    rule: 'القواعد',
  },
  nodeTypes: {
    passage: 'نص',
    sentence: 'جملة',
    word: 'كلمة',
    kanji: 'كانجي',
    particle: 'أداة',
    rule: 'قاعدة',
  },
  statuses: {
    stub: 'مسودة',
    generating: 'قيد الإنشاء',
    needs_review: 'بحاجة إلى مراجعة',
    published: 'منشور',
  },

  explore: {
    shuffle: 'خلط',
    loadFailed: 'تعذّر التحميل. حاول مرة أخرى بعد قليل.',
    emptyText: 'تظهر هنا النصوص المُدخلة والعناصر المُنشأة منها.',
    emptyTitles: {
      passage: 'لا توجد نصوص بعد',
      sentence: 'لا توجد جمل بعد',
      word: 'لا توجد كلمات بعد',
      kanji: 'لا توجد حروف كانجي بعد',
      particle: 'لا توجد أدوات بعد',
      rule: 'لا توجد قواعد بعد',
    },
  },

  speak: {
    readAloud: 'القراءة بصوت عالٍ باليابانية',
    stop: 'إيقاف',
    loop: 'تكرار',
    loopOn: 'التكرار مفعّل',
  },

  detail: {
    loading: 'جارٍ التحميل',
    notFound: 'لم يتم العثور على العقدة.',
    backToJapanese: 'العودة إلى اليابانية',
    radicals: 'الجذور: {radicals}',
    noContent: 'لا يوجد محتوى بعد.',
    noContentAdmin: 'لا يوجد محتوى بعد. انقر على «إنشاء المحتوى» لإنشائه.',
    linksFrom: 'روابط من هذه العقدة',
    linksTo: 'روابط إلى هذه العقدة',
    outgoing: {
      contains: 'يحتوي على',
      composed_of: 'يتكون من',
      uses_rule: 'يستخدم القاعدة',
      example_of: 'مثال على',
      exception_to: 'استثناء من',
      synonym_of: 'مرادف لـ',
      related_to: 'ذو صلة',
      same_kanji_as: 'نفس الكانجي مثل',
    },
    incoming: {
      contains: 'يظهر في',
      composed_of: 'مستخدم في كلمات',
      uses_rule: 'جمل تستخدم هذه القاعدة',
      example_of: 'أمثلة',
      exception_to: 'استثناءات',
      synonym_of: 'مرادفات',
      related_to: 'ذو صلة',
      same_kanji_as: 'نفس الكانجي مثل',
    },

    editTitle: 'تعديل العنوان',
    generateContent: 'إنشاء المحتوى',
    approve: 'اعتماد',
    regenerate: 'إعادة الإنشاء',
    generateDialog: {
      text: 'ملاحظات اختيارية لتوجيه النموذج (مثل «استخدم صيغة الكانجي 中»، «عامِل هذا كاسم لا كفعل»، «هذه هي الرابطة المهذبة»). اتركها فارغة للإنشاء بالقواعد الافتراضية.',
      label: 'ملاحظات (اختيارية)',
      confirm: 'إنشاء',
    },
    editTitleDialog: {
      text: 'حدّث النص الرئيسي المعروض لهذه العقدة. في الكلمات والجمل يمكنك إضافة الفوريغانا مثل 漢字(かんじ).',
      label: 'العنوان',
      confirm: 'حفظ',
    },
    error: 'خطأ',
    generateFailed: 'تعذّر إنشاء المحتوى: {error}',
    updateTitleFailed: 'تعذّر تحديث العنوان: {error}',
    approveFailed: 'تعذّر الاعتماد: {error}',
  },
};
