import {JapaneseStrings} from './en';

export const he: JapaneseStrings = {
  title: 'יפנית',
  subtitle: 'לחקור רשת של קטעים, משפטים, מילים, קאנג׳י, מיליות וכללי דקדוק.',
  nav: {
    explore: 'גילוי',
    ingest: 'קליטה',
    review: 'סקירה',
  },
  tabs: {
    passage: 'קטעים',
    sentence: 'משפטים',
    word: 'מילים',
    kanji: 'קאנג׳י',
    particle: 'מיליות',
    rule: 'כללים',
  },
  nodeTypes: {
    passage: 'קטע',
    sentence: 'משפט',
    word: 'מילה',
    kanji: 'קאנג׳י',
    particle: 'מילית',
    rule: 'כלל',
  },
  statuses: {
    stub: 'שלד',
    generating: 'בייצור',
    needs_review: 'ממתין לסקירה',
    published: 'פורסם',
  },

  explore: {
    shuffle: 'ערבוב',
    loadFailed: 'הטעינה נכשלה. כדאי לנסות שוב בעוד רגע.',
    emptyText: 'טקסטים שנקלטו והפריטים שנוצרו מהם יופיעו כאן.',
    emptyTitles: {
      passage: 'עדיין אין קטעים',
      sentence: 'עדיין אין משפטים',
      word: 'עדיין אין מילים',
      kanji: 'עדיין אין קאנג׳י',
      particle: 'עדיין אין מיליות',
      rule: 'עדיין אין כללים',
    },
  },

  speak: {
    readAloud: 'הקראה ביפנית',
    stop: 'עצירה',
    loop: 'חזרה',
    loopOn: 'חזרה פעילה',
  },

  detail: {
    loading: 'טוען',
    notFound: 'הצומת לא נמצא.',
    backToJapanese: 'חזרה ליפנית',
    radicals: 'רדיקלים: {radicals}',
    noContent: 'עדיין אין תוכן.',
    noContentAdmin: 'עדיין אין תוכן. לחיצה על ״יצירת תוכן״ תיצור אותו.',
    linksFrom: 'קישורים מהצומת הזה',
    linksTo: 'קישורים לצומת הזה',
    outgoing: {
      contains: 'מכיל',
      composed_of: 'מורכב מ',
      uses_rule: 'משתמש בכלל',
      example_of: 'דוגמה ל',
      exception_to: 'חריג ל',
      synonym_of: 'נרדף ל',
      related_to: 'קשור',
      same_kanji_as: 'אותו קאנג׳י כמו',
    },
    incoming: {
      contains: 'מופיע ב',
      composed_of: 'משמש במילים',
      uses_rule: 'משפטים שמשתמשים בכלל',
      example_of: 'דוגמאות',
      exception_to: 'חריגים',
      synonym_of: 'מילים נרדפות',
      related_to: 'קשור',
      same_kanji_as: 'אותו קאנג׳י כמו',
    },

    editTitle: 'עריכת כותרת',
    generateContent: 'יצירת תוכן',
    approve: 'אישור',
    regenerate: 'יצירה מחדש',
    generateDialog: {
      text: 'הערות אופציונליות להכוונת המודל (למשל ״להשתמש בצורת הקאנג׳י 中״, ״להתייחס לזה כשם עצם, לא כפועל״, ״זה האוגד המנומס״). אפשר להשאיר ריק כדי ליצור לפי הכללים הרגילים.',
      label: 'הערות (לא חובה)',
      confirm: 'יצירה',
    },
    editTitleDialog: {
      text: 'עדכון הטקסט הראשי שמוצג לצומת הזה. במילים ובמשפטים אפשר לכלול פוריגנה, למשל 漢字(かんじ).',
      label: 'כותרת',
      confirm: 'שמירה',
    },
    error: 'שגיאה',
    generateFailed: 'יצירת התוכן נכשלה: {error}',
    updateTitleFailed: 'עדכון הכותרת נכשל: {error}',
    approveFailed: 'האישור נכשל: {error}',
  },
};
