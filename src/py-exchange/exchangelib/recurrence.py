import logging

from .fields import (
    MONTHS,
    WEEK_NUMBERS,
    WEEKDAY_NAMES,
    WEEKDAYS,
    DateOrDateTimeField,
    DateTimeField,
    EnumField,
    EWSElementField,
    IdElementField,
    IntegerField,
    WeekdaysField,
)
from .properties import EWSElement, EWSMeta, IdChangeKeyMixIn, ItemId

log = logging.getLogger(__name__)


def _month_to_str(month):
    return MONTHS[month - 1] if isinstance(month, int) else month


def _weekday_to_str(weekday):
    return WEEKDAYS[weekday - 1] if isinstance(weekday, int) else weekday


def _week_number_to_str(week_number):
    return WEEK_NUMBERS[week_number - 1] if isinstance(week_number, int) else week_number


class Pattern(EWSElement, metaclass=EWSMeta):
    """Base class for all classes implementing recurring pattern elements."""


class Regeneration(Pattern, metaclass=EWSMeta):
    """Base class for all classes implementing recurring regeneration elements."""


class AbsoluteYearlyPattern(Pattern):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/absoluteyearlyrecurrence
    """

    ELEMENT_NAME = "AbsoluteYearlyRecurrence"

    # The day of month of an occurrence, in range 1 -> 31. If a particular month has less days than the day_of_month
    # value, the last day in the month is assumed
    day_of_month = IntegerField(field_uri="DayOfMonth", min=1, max=31, is_required=True)
    # The month of the year, from 1 - 12
    month = EnumField(field_uri="Month", enum=MONTHS, is_required=True)

    def __str__(self):
        return f"Occurs on day {self.day_of_month} of {_month_to_str(self.month)}"


class RelativeYearlyPattern(Pattern):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/relativeyearlyrecurrence
    """

    ELEMENT_NAME = "RelativeYearlyRecurrence"

    # Valid ISO 8601 weekday, as a number in range 1 -> 7 (1 being Monday). The value can also be one of the DAY
    # (or 8), WEEK_DAY (or 9) or WEEKEND_DAY (or 10) consts which is interpreted as the first day, weekday, or weekend
    # day of the year. Despite the field name in EWS, this is not a list.
    weekday = EnumField(field_uri="DaysOfWeek", enum=WEEKDAYS, is_required=True)
    # Week number of the month, in range 1 -> 5. If 5 is specified, this assumes the last week of the month for
    # months that have only 4 weeks
    week_number = EnumField(field_uri="DayOfWeekIndex", enum=WEEK_NUMBERS, is_required=True)
    # The month of the year, from 1 - 12
    month = EnumField(field_uri="Month", enum=MONTHS, is_required=True)

    def __str__(self):
        return (
            f"Occurs on weekday {_weekday_to_str(self.weekday)} in the {_week_number_to_str(self.week_number)} "
            f"week of {_month_to_str(self.month)}"
        )


class AbsoluteMonthlyPattern(Pattern):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/absolutemonthlyrecurrence
    """

    ELEMENT_NAME = "AbsoluteMonthlyRecurrence"

    # Interval, in months, in range 1 -> 99
    interval = IntegerField(field_uri="Interval", min=1, max=99, is_required=True)
    # The day of month of an occurrence, in range 1 -> 31. If a particular month has less days than the day_of_month
    # value, the last day in the month is assumed
    day_of_month = IntegerField(field_uri="DayOfMonth", min=1, max=31, is_required=True)

    def __str__(self):
        return f"Occurs on day {self.day_of_month} of every {self.interval} month(s)"


class RelativeMonthlyPattern(Pattern):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/relativemonthlyrecurrence
    """

    ELEMENT_NAME = "RelativeMonthlyRecurrence"

    # Interval, in months, in range 1 -> 99
    interval = IntegerField(field_uri="Interval", min=1, max=99, is_required=True)
    # Valid ISO 8601 weekday, as a number in range 1 -> 7 (1 being Monday). The value can also be one of the DAY
    # (or 8), WEEK_DAY (or 9) or WEEKEND_DAY (or 10) consts which is interpreted as the first day, weekday, or weekend
    # day of the month. Despite the field name in EWS, this is not a list.
    weekday = EnumField(field_uri="DaysOfWeek", enum=WEEKDAYS, is_required=True)
    # Week number of the month, in range 1 -> 5. If 5 is specified, this assumes the last week of the month for
    # months that have only 4 weeks.
    week_number = EnumField(field_uri="DayOfWeekIndex", enum=WEEK_NUMBERS, is_required=True)

    def __str__(self):
        return (
            f"Occurs on weekday {_weekday_to_str(self.weekday)} in the {_week_number_to_str(self.week_number)} "
            f"week of every {self.interval} month(s)"
        )


class WeeklyPattern(Pattern):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/weeklyrecurrence"""

    ELEMENT_NAME = "WeeklyRecurrence"

    # Interval, in weeks, in range 1 -> 99
    interval = IntegerField(field_uri="Interval", min=1, max=99, is_required=True)
    # List of valid ISO 8601 weekdays, as list of numbers in range 1 -> 7 (1 being Monday)
    weekdays = WeekdaysField(field_uri="DaysOfWeek", enum=WEEKDAY_NAMES, is_required=True)
    # The first day of the week. Defaults to Monday
    first_day_of_week = EnumField(field_uri="FirstDayOfWeek", enum=WEEKDAY_NAMES, default=1, is_required=True)

    def __str__(self):
        weekdays = [_weekday_to_str(i) for i in self.get_field_by_fieldname("weekdays").clean(self.weekdays)]
        return (
            f'Occurs on weekdays {", ".join(weekdays)} of every {self.interval} week(s) where the first day of '
            f"the week is {_weekday_to_str(self.first_day_of_week)}"
        )


class DailyPattern(Pattern):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/dailyrecurrence"""

    ELEMENT_NAME = "DailyRecurrence"

    # Interval, in days, in range 1 -> 999
    interval = IntegerField(field_uri="Interval", min=1, max=999, is_required=True)

    def __str__(self):
        return f"Occurs every {self.interval} day(s)"


class YearlyRegeneration(Regeneration):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/yearlyregeneration"""

    ELEMENT_NAME = "YearlyRegeneration"

    # Interval, in years
    interval = IntegerField(field_uri="Interval", min=1, is_required=True)

    def __str__(self):
        return f"Regenerates every {self.interval} year(s)"


class MonthlyRegeneration(Regeneration):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/monthlyregeneration"""

    ELEMENT_NAME = "MonthlyRegeneration"

    # Interval, in months
    interval = IntegerField(field_uri="Interval", min=1, is_required=True)

    def __str__(self):
        return f"Regenerates every {self.interval} month(s)"


class WeeklyRegeneration(Regeneration):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/weeklyregeneration"""

    ELEMENT_NAME = "WeeklyRegeneration"

    # Interval, in weeks
    interval = IntegerField(field_uri="Interval", min=1, is_required=True)

    def __str__(self):
        return f"Regenerates every {self.interval} week(s)"


class DailyRegeneration(Regeneration):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/dailyregeneration"""

    ELEMENT_NAME = "DailyRegeneration"

    # Interval, in days
    interval = IntegerField(field_uri="Interval", min=1, is_required=True)

    def __str__(self):
        return f"Regenerates every {self.interval} day(s)"


class Boundary(EWSElement, metaclass=EWSMeta):
    """Base class for all classes implementing recurring boundary elements."""


class NoEndPattern(Boundary):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/noendrecurrence"""

    ELEMENT_NAME = "NoEndRecurrence"

    # Start date, as EWSDate or EWSDateTime
    start = DateOrDateTimeField(field_uri="StartDate", is_required=True)

    def __str__(self):
        return f"Starts on {self.start}"


class EndDatePattern(Boundary):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/enddaterecurrence"""

    ELEMENT_NAME = "EndDateRecurrence"

    # Start date, as EWSDate or EWSDateTime
    start = DateOrDateTimeField(field_uri="StartDate", is_required=True)
    # End date, as EWSDate
    end = DateOrDateTimeField(field_uri="EndDate", is_required=True)

    def __str__(self):
        return f"Starts on {self.start}, ends on {self.end}"


class NumberedPattern(Boundary):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/numberedrecurrence"""

    ELEMENT_NAME = "NumberedRecurrence"

    # Start date, as EWSDate or EWSDateTime
    start = DateOrDateTimeField(field_uri="StartDate", is_required=True)
    # The number of occurrences in this pattern, in range 1 -> 999
    number = IntegerField(field_uri="NumberOfOccurrences", min=1, max=999, is_required=True)

    def __str__(self):
        return f"Starts on {self.start} and occurs {self.number} time(s)"


class Occurrence(IdChangeKeyMixIn):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/occurrence"""

    ELEMENT_NAME = "Occurrence"
    ID_ELEMENT_CLS = ItemId

    _id = IdElementField(field_uri="ItemId", value_cls=ID_ELEMENT_CLS)
    # The modified start time of the item, as EWSDateTime
    start = DateTimeField(field_uri="Start")
    # The modified end time of the item, as EWSDateTime
    end = DateTimeField(field_uri="End")
    # The original start time of the item, as EWSDateTime
    original_start = DateTimeField(field_uri="OriginalStart")


# Container elements:
# 'ModifiedOccurrences'
# 'DeletedOccurrences'


class FirstOccurrence(Occurrence):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/firstoccurrence"""

    ELEMENT_NAME = "FirstOccurrence"


class LastOccurrence(Occurrence):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/lastoccurrence"""

    ELEMENT_NAME = "LastOccurrence"


class DeletedOccurrence(EWSElement):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/deletedoccurrence"""

    ELEMENT_NAME = "DeletedOccurrence"

    # The modified start time of the item, as EWSDateTime
    start = DateTimeField(field_uri="Start")


PATTERN_CLASSES = (
    AbsoluteYearlyPattern,
    RelativeYearlyPattern,
    AbsoluteMonthlyPattern,
    RelativeMonthlyPattern,
    WeeklyPattern,
    DailyPattern,
)
REGENERATION_CLASSES = YearlyRegeneration, MonthlyRegeneration, WeeklyRegeneration, DailyRegeneration
BOUNDARY_CLASSES = NoEndPattern, EndDatePattern, NumberedPattern


class Recurrence(EWSElement):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/recurrence-recurrencetype
    """

    ELEMENT_NAME = "Recurrence"
    PATTERN_CLASS_MAP = {cls.response_tag(): cls for cls in PATTERN_CLASSES}
    BOUNDARY_CLASS_MAP = {cls.response_tag(): cls for cls in BOUNDARY_CLASSES}

    pattern = EWSElementField(value_cls=Pattern)
    boundary = EWSElementField(value_cls=Boundary)

    def __init__(self, **kwargs):
        # Allow specifying a start, end and/or number as a shortcut to creating a boundary
        start = kwargs.pop("start", None)
        end = kwargs.pop("end", None)
        number = kwargs.pop("number", None)
        if any([start, end, number]):
            if "boundary" in kwargs:
                raise ValueError("'boundary' is not allowed in combination with 'start', 'end' or 'number'")
            if start and not end and not number:
                kwargs["boundary"] = NoEndPattern(start=start)
            elif start and end and not number:
                kwargs["boundary"] = EndDatePattern(start=start, end=end)
            elif start and number and not end:
                kwargs["boundary"] = NumberedPattern(start=start, number=number)
            else:
                raise ValueError("Unsupported 'start', 'end', 'number' combination")
        super().__init__(**kwargs)

    @classmethod
    def from_xml(cls, elem, account):
        pattern, boundary = None, None
        for child_elem in elem:
            if child_elem.tag in cls.PATTERN_CLASS_MAP:
                pattern = cls.PATTERN_CLASS_MAP[child_elem.tag].from_xml(elem=child_elem, account=account)
            elif child_elem.tag in cls.BOUNDARY_CLASS_MAP:
                boundary = cls.BOUNDARY_CLASS_MAP[child_elem.tag].from_xml(elem=child_elem, account=account)
        return cls(pattern=pattern, boundary=boundary)

    def __str__(self):
        return f"Pattern: {self.pattern}, Boundary: {self.boundary}"


class TaskRecurrence(Recurrence):
    """MSDN:
    https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/recurrence-taskrecurrencetype
    """

    PATTERN_CLASS_MAP = {cls.response_tag(): cls for cls in PATTERN_CLASSES + REGENERATION_CLASSES}
