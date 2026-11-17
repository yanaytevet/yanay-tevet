import {Language} from '../../../generated-files/api/users';

// Strings for the parts of the site every user sees: the top bar, the left drawer, the footer, the home
// page and account settings. Each app keeps its own strings (workout-plan/shared/workout-strings.ts).
export interface ChromeStrings {
  // Top bar, drawer and footer
  home: string;
  signIn: string;
  faq: string;
  contact: string;
  privacy: string;
  terms: string;
  privacyPolicy: string;
  termsAndConditions: string;
  about: string;
  admin: string;
  ingest: string;
  reviewQueue: string;
  apartmentHunt: string;
  villaVillekulla: string;
  rentersCrm: string;
  userManagement: string;
  user: string;
  accountSettings: string;
  managePasskeys: string;
  logout: string;
  theme: string;

  // Home
  welcome: string;
  welcomeSub: string;
  publicApps: string;
  yourApps: string;
  learnMore: string;
  heroSub: string;
  tryForFree: string;
  descriptions: {
    genre: string;
    japanese: string;
    japaneseShort: string;
    dates: string;
    datesShort: string;
    tasks: string;
    shopping: string;
    itinerary: string;
    home: string;
    workout: string;
    dreams: string;
    pdf: string;
    dashboard: string;
    userManagement: string;
  };

  // Account settings
  settingsTitle: string;
  language: string;
  languageHint: string;
  profileImage: string;
  uploading: string;
  changePhoto: string;
  profileDetails: string;
  firstName: string;
  lastName: string;
  emailAddress: string;
  saving: string;
  saveChanges: string;
  timezone: string;
  timezoneHint: string;
  close: string;
  change: string;
  searchTimezones: string;
  noTimezones: string;
  usingBrowserTimezone: string;
  browserDetected: string;
  useBrowserTimezone: string;
  connectClaude: string;
  connectClaudeHintBefore: string;
  connectClaudeHintAfter: string;
  loading: string;
  notReachable: string;
  connectorUrl: string;
  copied: string;
  copy: string;
  addToClaude: string;
  connectionUnavailable: string;
  changePassword: string;
  setPassword: string;
  noPasswordHint: string;
  currentPassword: string;
  newPassword: string;
  confirmNewPassword: string;
  passwordsDontMatch: string;
  passwordChanged: string;
  changing: string;
  needHelp: string;
  needHelpText: string;
  passkeys: string;
  passkey: string;
  added: string;
  removing: string;
  remove: string;
  noPasskeys: string;
  maxPasskeys: string;
  registering: string;
  registerPasskey: string;
  passwordRules: {
    length: string;
    upper: string;
    lower: string;
    digit: string;
  };
}

export const CHROME_STRINGS: Record<Language, ChromeStrings> = {
  en: {
    home: 'Home',
    signIn: 'Sign in',
    faq: 'FAQ',
    contact: 'Contact',
    privacy: 'Privacy',
    terms: 'Terms',
    privacyPolicy: 'Privacy Policy',
    termsAndConditions: 'Terms & Conditions',
    about: 'About',
    admin: 'Admin',
    ingest: 'Ingest',
    reviewQueue: 'Review Queue',
    apartmentHunt: 'Apartment Hunt',
    villaVillekulla: 'Villa Villekulla',
    rentersCrm: 'Renters CRM',
    userManagement: 'User Management',
    user: 'User',
    accountSettings: 'Account Settings',
    managePasskeys: 'Manage Passkeys',
    logout: 'Logout',
    theme: 'Theme',

    welcome: 'Welcome to Yanay Tevet\'s Platform',
    welcomeSub: 'This is where I build stuff.',
    publicApps: 'Public apps',
    yourApps: 'Your apps',
    learnMore: 'Learn more',
    heroSub: 'My projects — some public, some not.',
    tryForFree: 'Try for free',
    descriptions: {
      genre: 'Train your ear on electronic music genres',
      japanese: 'Explore Japanese through a network of sentences, words, kanji, and rules',
      japaneseShort: 'Explore Japanese through a network of nodes',
      dates: 'Birthdays, anniversaries and memorials — in Hebrew and Gregorian dates',
      datesShort: 'Birthdays and anniversaries in Hebrew and Gregorian dates',
      tasks: 'Projects, tasks and subtasks with due dates, priorities and sharing',
      shopping: 'Shared grocery lists — check items off and re-add them from history',
      itinerary: 'Reusable packing and prep lists you activate when you head out',
      home: 'Find your next place — hunt apartments, track villas, and manage renters',
      workout: 'Training plans, logged sets with a rest timer, and graphs of your progress',
      dreams: 'Log and explore your dreams',
      pdf: 'Edit text, fill forms, sign and rearrange pages — files never leave your browser',
      dashboard: 'Live status from the services I depend on',
      userManagement: 'View users and grant or revoke permissions',
    },

    settingsTitle: 'Account settings',
    language: 'Language',
    languageHint: 'The language of the menus, the home page and the apps that are translated. Other apps stay in English for now.',
    profileImage: 'Profile Image',
    uploading: 'Uploading...',
    changePhoto: 'Change Photo',
    profileDetails: 'Profile Details',
    firstName: 'First Name',
    lastName: 'Last Name',
    emailAddress: 'Email Address',
    saving: 'Saving...',
    saveChanges: 'Save Changes',
    timezone: 'Timezone',
    timezoneHint: 'Repeating tasks in projects you own reset to "To do" at 4:00 AM in this timezone.',
    close: 'Close',
    change: 'Change',
    searchTimezones: 'Search timezones...',
    noTimezones: 'No timezones match',
    usingBrowserTimezone: 'Using your browser\'s timezone.',
    browserDetected: 'Browser detected:',
    useBrowserTimezone: 'Use browser timezone',
    connectClaude: 'Connect to Claude',
    connectClaudeHintBefore: 'Add this site as a connector in Claude to manage your tasks, shopping lists and workout plans from a chat. Click',
    connectClaudeHintAfter: ', then confirm in Claude — you\'ll sign in with your account here. You don\'t need to fill in any OAuth fields; if the URL isn\'t already filled in, paste the one below.',
    loading: 'Loading…',
    notReachable: 'The server isn\'t publicly reachable: MCP_PUBLIC_BASE_URL isn\'t configured on the backend. In development, start a tunnel (ngrok) and restart the backend instead.',
    connectorUrl: 'Connector URL',
    copied: 'Copied',
    copy: 'Copy',
    addToClaude: 'Add to Claude',
    connectionUnavailable: 'Connection info unavailable.',
    changePassword: 'Change Password',
    setPassword: 'Set Password',
    noPasswordHint: 'Your account doesn\'t have a password set. You can set one here to also be able to log in with email and password.',
    currentPassword: 'Current Password',
    newPassword: 'New Password',
    confirmNewPassword: 'Confirm New Password',
    passwordsDontMatch: 'Passwords do not match',
    passwordChanged: 'Password changed successfully',
    changing: 'Changing...',
    needHelp: 'Need Help?',
    needHelpText: 'If you have questions or run into any issues, contact us at',
    passkeys: 'Passkeys',
    passkey: 'Passkey',
    added: 'Added',
    removing: 'Removing...',
    remove: 'Remove',
    noPasskeys: 'No passkeys registered.',
    maxPasskeys: 'Maximum of 3 passkeys reached.',
    registering: 'Registering...',
    registerPasskey: 'Register New Passkey',
    passwordRules: {
      length: 'At least 8 characters',
      upper: 'An uppercase letter',
      lower: 'A lowercase letter',
      digit: 'A digit',
    },
  },
  he: {
    home: 'דף הבית',
    signIn: 'התחברות',
    faq: 'שאלות נפוצות',
    contact: 'יצירת קשר',
    privacy: 'פרטיות',
    terms: 'תנאים',
    privacyPolicy: 'מדיניות פרטיות',
    termsAndConditions: 'תנאי שימוש',
    about: 'אודות',
    admin: 'ניהול',
    ingest: 'קליטה',
    reviewQueue: 'תור סקירה',
    apartmentHunt: 'חיפוש דירה',
    villaVillekulla: 'וילה וילקולה',
    rentersCrm: 'ניהול שוכרים',
    userManagement: 'ניהול משתמשים',
    user: 'משתמש',
    accountSettings: 'הגדרות חשבון',
    managePasskeys: 'ניהול מפתחות גישה',
    logout: 'התנתקות',
    theme: 'ערכת צבעים',

    welcome: 'ברוכים הבאים לפלטפורמה של ינאי טבת',
    welcomeSub: 'כאן אני בונה דברים.',
    publicApps: 'אפליקציות ציבוריות',
    yourApps: 'האפליקציות שלך',
    learnMore: 'מידע נוסף',
    heroSub: 'הפרויקטים שלי — חלקם ציבוריים, חלקם לא.',
    tryForFree: 'נסו בחינם',
    descriptions: {
      genre: 'אימון שמיעה לז׳אנרים של מוזיקה אלקטרונית',
      japanese: 'לימוד יפנית דרך רשת של משפטים, מילים, קאנג׳י וחוקים',
      japaneseShort: 'לימוד יפנית דרך רשת של צמתים',
      dates: 'ימי הולדת, ימי נישואין וימי זיכרון — בתאריך עברי ולועזי',
      datesShort: 'ימי הולדת וימי נישואין בתאריך עברי ולועזי',
      tasks: 'פרויקטים, משימות ותתי־משימות עם תאריכי יעד, עדיפויות ושיתוף',
      shopping: 'רשימות קניות משותפות — מסמנים פריטים ומחזירים אותם מההיסטוריה',
      itinerary: 'רשימות אריזה והכנה שאפשר להפעיל שוב לפני כל יציאה',
      home: 'מוצאים את המקום הבא — חיפוש דירות, מעקב וילות וניהול שוכרים',
      workout: 'תוכניות אימון, תיעוד סטים עם טיימר מנוחה, וגרפים של ההתקדמות',
      dreams: 'תיעוד וחקירה של החלומות שלך',
      pdf: 'עריכת טקסט, מילוי טפסים, חתימה וסידור עמודים — הקבצים לא יוצאים מהדפדפן',
      dashboard: 'סטטוס חי מהשירותים שאני תלוי בהם',
      userManagement: 'צפייה במשתמשים והענקה או ביטול של הרשאות',
    },

    settingsTitle: 'הגדרות חשבון',
    language: 'שפה',
    languageHint: 'שפת התפריטים, דף הבית והאפליקציות שתורגמו. שאר האפליקציות נשארות באנגלית בינתיים.',
    profileImage: 'תמונת פרופיל',
    uploading: 'מעלה...',
    changePhoto: 'החלפת תמונה',
    profileDetails: 'פרטי פרופיל',
    firstName: 'שם פרטי',
    lastName: 'שם משפחה',
    emailAddress: 'כתובת אימייל',
    saving: 'שומר...',
    saveChanges: 'שמירת שינויים',
    timezone: 'אזור זמן',
    timezoneHint: 'משימות חוזרות בפרויקטים שלך חוזרות ל״לביצוע״ ב־4:00 לפנות בוקר באזור הזמן הזה.',
    close: 'סגירה',
    change: 'שינוי',
    searchTimezones: 'חיפוש אזור זמן...',
    noTimezones: 'אין אזור זמן שמתאים ל',
    usingBrowserTimezone: 'משתמש באזור הזמן של הדפדפן.',
    browserDetected: 'הדפדפן זיהה:',
    useBrowserTimezone: 'שימוש באזור הזמן של הדפדפן',
    connectClaude: 'חיבור ל־Claude',
    connectClaudeHintBefore: 'הוסיפו את האתר כ־connector ב־Claude כדי לנהל משימות, רשימות קניות ותוכניות אימון מתוך שיחה. לחצו על',
    connectClaudeHintAfter: ', ואשרו ב־Claude — תתחברו עם החשבון שלכם כאן. אין צורך למלא שדות OAuth; אם הכתובת לא מולאה, הדביקו את זו שלמטה.',
    loading: 'טוען…',
    notReachable: 'השרת לא נגיש מבחוץ: MCP_PUBLIC_BASE_URL לא מוגדר בשרת. בפיתוח, הפעילו tunnel (ngrok) ואתחלו את השרת.',
    connectorUrl: 'כתובת ה־connector',
    copied: 'הועתק',
    copy: 'העתקה',
    addToClaude: 'הוספה ל־Claude',
    connectionUnavailable: 'פרטי החיבור לא זמינים.',
    changePassword: 'שינוי סיסמה',
    setPassword: 'הגדרת סיסמה',
    noPasswordHint: 'לחשבון שלך אין סיסמה. אפשר להגדיר אחת כאן כדי להתחבר גם עם אימייל וסיסמה.',
    currentPassword: 'סיסמה נוכחית',
    newPassword: 'סיסמה חדשה',
    confirmNewPassword: 'אימות סיסמה חדשה',
    passwordsDontMatch: 'הסיסמאות לא תואמות',
    passwordChanged: 'הסיסמה שונתה',
    changing: 'משנה...',
    needHelp: 'צריכים עזרה?',
    needHelpText: 'יש שאלות או בעיה? כתבו לנו ל־',
    passkeys: 'מפתחות גישה',
    passkey: 'מפתח גישה',
    added: 'נוסף',
    removing: 'מסיר...',
    remove: 'הסרה',
    noPasskeys: 'אין מפתחות גישה רשומים.',
    maxPasskeys: 'הגעת למקסימום של 3 מפתחות גישה.',
    registering: 'רושם...',
    registerPasskey: 'רישום מפתח גישה חדש',
    passwordRules: {
      length: 'לפחות 8 תווים',
      upper: 'אות גדולה באנגלית',
      lower: 'אות קטנה באנגלית',
      digit: 'ספרה',
    },
  },
};
