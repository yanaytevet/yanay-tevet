import calendar
import math
from datetime import datetime, timedelta, date

import pytz
from tzlocal import get_localzone

TimeType = datetime
DateType = date
TimeDeltaType = timedelta


class TimeUtils:
    LOCAL_TZ = get_localzone()
    DEFAULT_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'

    @classmethod
    def now(cls) -> TimeType:
        return datetime.now().astimezone(cls.LOCAL_TZ)

    @staticmethod
    def start_of_month(dt) -> TimeType:
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    @classmethod
    def now_epoch(cls) -> float:
        return (cls.now() - cls.zero_time()).total_seconds()

    @classmethod
    def today(cls) -> DateType:
        return date.today()

    @classmethod
    def now_rounded_half_hour(cls) -> TimeType:
        return cls.ceil_time(cls.now(), 30)

    @classmethod
    def ceil_time(cls, time: TimeType, delta_minutes: int) -> TimeType:
        hour_start = time.replace(microsecond=0, second=0, minute=0)
        delta = time - hour_start
        minutes = int(math.ceil((delta.total_seconds() / 60) / delta_minutes)) * delta_minutes
        return hour_start + timedelta(minutes=minutes)

    @classmethod
    def create_aware_datetime(cls, *args, **kwargs) -> TimeType:
        date_obj = datetime(*args, **kwargs)
        return cls.make_aware(date_obj)

    @classmethod
    def zero_time(cls) -> TimeType:
        date_obj = datetime(1970, 1, 1)
        return cls.make_aware(datetime_obj=date_obj, timezone='utc')

    @classmethod
    def inf_time(cls) -> TimeType:
        date_obj = datetime(3000, 1, 1)
        return cls.make_aware(datetime_obj=date_obj, timezone='utc')

    @classmethod
    def to_format_str(cls, datetime_obj: TimeType | None, date_format: str) -> str | None:
        if datetime_obj is None or date_format is None:
            return None
        return datetime_obj.strftime(date_format)

    @classmethod
    def from_format_str(cls, datetime_str: str, date_format: str, timezone: str | None = None) -> TimeType | None:
        if datetime_str is None:
            return None
        raw_time = datetime.strptime(datetime_str, date_format)
        return cls.make_aware(raw_time, timezone=timezone)

    @classmethod
    def from_default_str(cls, datetime_str: str) -> TimeType | None:
        return cls.from_format_str(datetime_str, cls.DEFAULT_FORMAT)

    @classmethod
    def to_default_str(cls, datetime_obj: TimeType | None) -> str | None:
        if datetime_obj is None:
            return None
        return datetime_obj.strftime(cls.DEFAULT_FORMAT)

    @classmethod
    def create_to_default_str(cls, *args, **kwargs) -> str | None:
        return cls.to_default_str(cls.create_aware_datetime(*args, **kwargs))

    @classmethod
    def make_aware(cls, datetime_obj: TimeType, timezone: str | None = None) -> TimeType:
        if cls.is_aware(datetime_obj):
            return datetime_obj
        if timezone:
            timezone_obj = pytz.timezone(timezone)
        else:
            timezone_obj = cls.LOCAL_TZ
        return datetime_obj.astimezone(timezone_obj)

    @classmethod
    def is_aware(cls, datetime_obj: TimeType) -> TimeType:
        return datetime_obj.tzinfo is not None and datetime_obj.tzinfo.utcoffset(datetime_obj) is not None

    @classmethod
    def seconds_since_epoch(cls, datetime_obj: TimeType) -> float:
        return (datetime_obj - cls.zero_time()).total_seconds()

    @classmethod
    def time_from_seconds_since_epoch(cls, total_seconds: float) -> TimeType:
        return cls.make_aware(datetime.utcfromtimestamp(total_seconds))

    @classmethod
    def add_years_to_time(cls, time_obj: TimeType, years: int) -> TimeType:
        new_year = time_obj.year + years
        last_day = calendar.monthrange(new_year, time_obj.month)[1]
        return cls.create_aware_datetime(time_obj.year + years, time_obj.month, min(time_obj.day, last_day))

    @classmethod
    def add_months_to_time(cls, time_obj: TimeType, months: int) -> TimeType:
        total_months = time_obj.month + months - 1
        add_years = total_months // 12
        new_months = total_months % 12 + 1
        new_year = time_obj.year + add_years
        last_day = calendar.monthrange(new_year, new_months)[1]
        day = min(time_obj.day, last_day)
        return cls.create_aware_datetime(new_year, new_months, day)

    @classmethod
    def add_days_to_time(cls, time_obj: TimeType, days: int) -> TimeType:
        return time_obj + timedelta(days=days)

    @classmethod
    def add_hours_to_time(cls, time_obj: TimeType, hours: int) -> TimeType:
        return time_obj + timedelta(hours=hours)

    @classmethod
    def add_minutes_to_time(cls, time_obj: TimeType, minutes: int) -> TimeType:
        return time_obj + timedelta(minutes=minutes)

    @classmethod
    def add_seconds_to_time(cls, time_obj: TimeType, seconds: int) -> TimeType:
        return time_obj + timedelta(seconds=seconds)

    @classmethod
    def add_years_to_now(cls, years: int) -> TimeType:
        return cls.add_years_to_time(cls.now(), years)

    @classmethod
    def add_months_to_now(cls, months: int) -> TimeType:
        return cls.add_months_to_time(cls.now(), months)

    @classmethod
    def add_days_to_now(cls, days: int) -> TimeType:
        return cls.add_days_to_time(cls.now(), days)

    @classmethod
    def add_hours_to_now(cls, hours: int) -> TimeType:
        return cls.add_hours_to_time(cls.now(), hours)

    @classmethod
    def add_minutes_to_now(cls, minutes: int) -> TimeType:
        return cls.add_minutes_to_time(cls.now(), minutes)

    @classmethod
    def add_seconds_to_now(cls, seconds: int) -> TimeType:
        return cls.add_seconds_to_time(cls.now(), seconds)

    @classmethod
    def remove_hours_from_date(cls, date_obj: TimeType) -> TimeType:
        return date_obj.replace(hour=0, minute=0, second=0, microsecond=0)

    @classmethod
    def date_to_datetime(cls, date_obj: date) -> TimeType:
        return cls.make_aware(datetime.combine(date_obj, datetime.min.time()))

    @classmethod
    def get_month_end_time(cls, date_obj: TimeType) -> TimeType:
        year = date_obj.year
        month = date_obj.month
        return cls.get_last_day_in_month(year=year, month=month)

    @classmethod
    def get_last_day_in_month(cls, year: int, month: int) -> TimeType:
        last_day = calendar.monthrange(year, month)[1]
        return cls.create_aware_datetime(year, month, last_day)

    @classmethod
    def get_first_day_in_month_date(cls, year: int, month: int) -> TimeType:
        return cls.create_aware_datetime(year, month, 1)

    @classmethod
    def get_first_day_in_month_from_time_obj(cls, date_obj: TimeType) -> TimeType:
        return cls.get_first_day_in_month_date(year=date_obj.year, month=date_obj.month)

    @classmethod
    def timedelta_to_seconds(cls, time_delta: timedelta) -> float:
        return time_delta.total_seconds()

    @classmethod
    def timedelta_to_days(cls, time_delta: timedelta) -> float:
        time_delta_sec = cls.timedelta_to_seconds(time_delta=time_delta)
        return time_delta_sec / (24 * 60 * 60)

    @classmethod
    def timedelta_from_days(cls, days: float) -> TimeDeltaType:
        return timedelta(seconds=days * 24 * 60 * 60)

    @classmethod
    def add_time_zone_offset(cls, time: TimeType, timezone_name: str) -> TimeType:
        timezone_info = pytz.timezone(timezone_name)
        return time.astimezone(timezone_info)

    @classmethod
    def get_time_zone_offset(cls, timezone_name: str) -> str:
        time_obj = cls.add_time_zone_offset(cls.now(), timezone_name)
        return time_obj.strftime('%z')

    @classmethod
    def years_from_now(cls, time: datetime) -> float:
        now = cls.now()
        df = now - time
        return df.total_seconds() / 60 / 60 / 24 / 365

    @classmethod
    def days_from_now(cls, time: datetime) -> float:
        now = cls.now()
        df = now - time
        return df.total_seconds() / 60 / 60 / 24

    @classmethod
    def hours_from_now(cls, time: datetime) -> float:
        now = cls.now()
        df = now - time
        return df.total_seconds() / 60 / 60

    @classmethod
    def minutes_from_now(cls, time: datetime) -> float:
        now = cls.now()
        df = now - time
        return df.total_seconds() / 60

    @classmethod
    def seconds_from_now(cls, time: datetime) -> float:
        now = cls.now()
        df = now - time
        return df.total_seconds()

    @classmethod
    def days_until_today_date(cls, date_obj: date) -> float:
        today = cls.today()
        df = today - date_obj
        return df.total_seconds() / 60 / 60 / 24
