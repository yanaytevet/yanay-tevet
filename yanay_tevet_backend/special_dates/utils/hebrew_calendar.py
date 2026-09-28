from dataclasses import dataclass
from datetime import date

# Arithmetic Hebrew calendar (Reingold & Dershowitz, "Calendrical Calculations").
# Fixed dates are Python ordinals (date.toordinal()), which equal R.D. numbers.
# Months are numbered from Nisan: 1=Nisan ... 7=Tishrei ... 12=Adar (Adar I in a leap year), 13=Adar II.

HEBREW_EPOCH = -1373427

NISAN = 1
TISHREI = 7
MARHESHVAN = 8
KISLEV = 9
ADAR = 12
ADAR_II = 13

MONTH_NAMES = {
    1: 'ניסן',
    2: 'אייר',
    3: 'סיוון',
    4: 'תמוז',
    5: 'אב',
    6: 'אלול',
    7: 'תשרי',
    8: 'חשוון',
    9: 'כסלו',
    10: 'טבת',
    11: 'שבט',
    12: 'אדר',
    13: 'אדר ב׳',
}
ADAR_I_NAME = 'אדר א׳'

GEMATRIA_ONES = ['', 'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט']
GEMATRIA_TENS = ['', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ']
GEMATRIA_HUNDREDS = ['', 'ק', 'ר', 'ש', 'ת']


@dataclass(frozen=True)
class HebrewDate:
    year: int
    month: int
    day: int


class HebrewCalendar:
    @staticmethod
    def is_leap_year(year: int) -> bool:
        return (7 * year + 1) % 19 < 7

    @staticmethod
    def last_month_of_year(year: int) -> int:
        return ADAR_II if HebrewCalendar.is_leap_year(year) else ADAR

    @staticmethod
    def _elapsed_days(year: int) -> int:
        months_elapsed = (235 * year - 234) // 19
        parts_elapsed = 12084 + 13753 * months_elapsed
        days = 29 * months_elapsed + parts_elapsed // 25920
        if (3 * (days + 1)) % 7 < 3:
            return days + 1
        return days

    @staticmethod
    def _year_length_correction(year: int) -> int:
        ny0 = HebrewCalendar._elapsed_days(year - 1)
        ny1 = HebrewCalendar._elapsed_days(year)
        ny2 = HebrewCalendar._elapsed_days(year + 1)
        if ny2 - ny1 == 356:
            return 2
        if ny1 - ny0 == 382:
            return 1
        return 0

    @staticmethod
    def new_year(year: int) -> int:
        return HEBREW_EPOCH + HebrewCalendar._elapsed_days(year) + HebrewCalendar._year_length_correction(year)

    @staticmethod
    def days_in_year(year: int) -> int:
        return HebrewCalendar.new_year(year + 1) - HebrewCalendar.new_year(year)

    @staticmethod
    def days_in_month(year: int, month: int) -> int:
        if month in (2, 4, 6, 10, ADAR_II):
            return 29
        if month == ADAR and not HebrewCalendar.is_leap_year(year):
            return 29
        year_length = HebrewCalendar.days_in_year(year)
        if month == MARHESHVAN and year_length % 10 != 5:
            return 29
        if month == KISLEV and year_length % 10 == 3:
            return 29
        return 30

    @staticmethod
    def to_ordinal(hebrew_date: HebrewDate) -> int:
        year, month, day = hebrew_date.year, hebrew_date.month, hebrew_date.day
        result = HebrewCalendar.new_year(year) + day - 1
        if month < TISHREI:
            for m in range(TISHREI, HebrewCalendar.last_month_of_year(year) + 1):
                result += HebrewCalendar.days_in_month(year, m)
            for m in range(NISAN, month):
                result += HebrewCalendar.days_in_month(year, m)
        else:
            for m in range(TISHREI, month):
                result += HebrewCalendar.days_in_month(year, m)
        return result

    @staticmethod
    def from_ordinal(ordinal: int) -> HebrewDate:
        approx = int((ordinal - HEBREW_EPOCH) // (35975351 / 98496)) + 1
        year = approx - 1
        while HebrewCalendar.new_year(year + 1) <= ordinal:
            year += 1
        first_nisan = HebrewCalendar.to_ordinal(HebrewDate(year, NISAN, 1))
        month = TISHREI if ordinal < first_nisan else NISAN
        while ordinal > HebrewCalendar.to_ordinal(HebrewDate(year, month, HebrewCalendar.days_in_month(year, month))):
            month += 1
        day = ordinal - HebrewCalendar.to_ordinal(HebrewDate(year, month, 1)) + 1
        return HebrewDate(year, month, day)

    @staticmethod
    def from_gregorian(gregorian: date) -> HebrewDate:
        return HebrewCalendar.from_ordinal(gregorian.toordinal())

    @staticmethod
    def to_gregorian(hebrew_date: HebrewDate) -> date:
        return date.fromordinal(HebrewCalendar.to_ordinal(hebrew_date))

    @staticmethod
    def anniversary_in_year(original: HebrewDate, year: int) -> HebrewDate:
        """The same Hebrew day in another year.

        Adar of a regular year maps to Adar II in a leap year (as with a bar mitzvah), both Adars of a
        leap year map to Adar in a regular year, and a 30th that doesn't exist that year becomes the 29th.
        """
        month = original.month
        target_is_leap = HebrewCalendar.is_leap_year(year)
        if month == ADAR and target_is_leap and not HebrewCalendar.is_leap_year(original.year):
            month = ADAR_II
        elif month == ADAR_II and not target_is_leap:
            month = ADAR
        day = min(original.day, HebrewCalendar.days_in_month(year, month))
        return HebrewDate(year, month, day)

    @staticmethod
    def months_in_year_order(year: int) -> list[int]:
        """Months in the order they occur in the year: Tishrei ... Adar (I, II) ... Elul."""
        return list(range(TISHREI, HebrewCalendar.last_month_of_year(year) + 1)) + list(range(NISAN, TISHREI))

    @staticmethod
    def is_valid(hebrew_date: HebrewDate) -> bool:
        if hebrew_date.month < NISAN or hebrew_date.month > HebrewCalendar.last_month_of_year(hebrew_date.year):
            return False
        return 1 <= hebrew_date.day <= HebrewCalendar.days_in_month(hebrew_date.year, hebrew_date.month)

    @staticmethod
    def month_name(year: int, month: int) -> str:
        if month == ADAR and HebrewCalendar.is_leap_year(year):
            return ADAR_I_NAME
        return MONTH_NAMES[month]

    @staticmethod
    def gematria(number: int) -> str:
        letters = ''
        hundreds = (number % 1000) // 100
        while hundreds >= 4:
            letters += GEMATRIA_HUNDREDS[4]
            hundreds -= 4
        letters += GEMATRIA_HUNDREDS[hundreds]
        rest = number % 100
        if rest == 15:
            letters += 'טו'
        elif rest == 16:
            letters += 'טז'
        else:
            letters += GEMATRIA_TENS[rest // 10] + GEMATRIA_ONES[rest % 10]
        if len(letters) == 1:
            return letters + '׳'
        return letters[:-1] + '״' + letters[-1]

    @staticmethod
    def format(hebrew_date: HebrewDate, with_year: bool = True) -> str:
        day = HebrewCalendar.gematria(hebrew_date.day)
        month = HebrewCalendar.month_name(hebrew_date.year, hebrew_date.month)
        if not with_year:
            return f'{day} ב{month}'
        return f'{day} ב{month} {HebrewCalendar.gematria(hebrew_date.year)}'
