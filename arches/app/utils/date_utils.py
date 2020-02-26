import calendar
import datetime
import dateutil
from dateutil.relativedelta import relativedelta
from edtf import parse_edtf, text_to_edtf
from edtf.parser.parser_classes import (
    Date,
    DateAndTime,
    Interval,
    Unspecified,
    UncertainOrApproximate,
    Level1Interval,
    LongYear,
    Season,
    PartialUncertainOrApproximate,
    PartialUnspecified,
    OneOfASet,
    MultipleDates,
    Level2Interval,
    ExponentialYear,
    PRECISION_YEAR,
    PRECISION_MONTH,
    PRECISION_DAY,
    EARLIEST,
    LATEST,
)


class SortableDateRange(object):
    def __init__(self):
        self.lower = None
        self.upper = None
        self.lower_fuzzy = None
        self.upper_fuzzy = None


class ExtendedDateFormat(SortableDateRange):
    def __init__(
        self,
        date=None,
        fuzzy_year_padding=1,
        fuzzy_month_padding=1,
        fuzzy_day_padding=1,
        fuzzy_season_padding=12,
        multiplier_if_uncertain=1,
        multiplier_if_approximate=1,
        multiplier_if_both=1,
    ):
        super(ExtendedDateFormat, self).__init__()
        self.orig_date = None
        self.edtf = None
        self.result_set = None
        self.sortable_date = None
        self.error = None
        self.fuzzy_year_padding = int(fuzzy_year_padding)
        self.fuzzy_month_padding = int(fuzzy_month_padding)
        self.fuzzy_day_padding = int(fuzzy_day_padding)
        self.fuzzy_season_padding = int(fuzzy_season_padding)

        self.multiplier_if_uncertain = int(multiplier_if_uncertain)
        self.multiplier_if_approximate = int(multiplier_if_approximate)
        self.multiplier_if_both = int(multiplier_if_both)

        try:
            self.parse(date)
        except Exception as e:
            try:
                self.parse(text_to_edtf(self.orig_date))
            except Exception as err:
                self.error = err
                raise err

    def parse(self, date=None):
        if date is None:
            return None

        self.edtf = None
        self.orig_date = date
        self.result_set = None
        self.error = None

        try:
            # handle for incorrectly formatted year only dates
            # (eg: 290 => 0290, 11909 => y11909)
            if int(date) >= 0:
                date = str(int(date)).zfill(4)
            else:
                date = str(int(date)).zfill(5)
            if len(str(abs(int(date)))) > 4 and int(date) != 0:
                date = "y" + date
        except Exception:
            pass

        self.edtf = parse_edtf(date)
        result = self.handle_object(self.edtf)
        if isinstance(result, list):
            self.result_set = result
        else:
            self.lower = result.lower
            self.upper = result.upper
            self.lower_fuzzy = result.lower_fuzzy
            self.upper_fuzzy = result.upper_fuzzy

    def is_valid(self):
        return True if self.lower or self.upper or self.lower_fuzzy or self.upper_fuzzy or self.result_set else False

    def is_leap_year(self, year):
        if ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0):
            return True
        return False

    def to_sortable_date(self, year=0, month=1, day=1):
        try:
            year = int(year) * 10000
            month = str(month).zfill(2)
            day = str(day).zfill(2)
            # return int("%s%s%s" % (self.year,month,day))
            return year + int("%s%s" % (month, day))
        except:
            return None

    def handle_object(self, object, fuzzy_padding=None):
        """
        Called to handle any date type, looks for the correct handling

        """

        if isinstance(object, Date) or isinstance(object, Season) or isinstance(object, Unspecified):
            if isinstance(object, PartialUncertainOrApproximate):
                fuzzy_padding = self.get_fuzzy_padding(object)
            return self.handle_date(object, fuzzy_padding)
        elif isinstance(object, UncertainOrApproximate):
            return self.handle_object(object.date, self.get_fuzzy_padding(object))
        elif isinstance(object, DateAndTime) or isinstance(object, PartialUnspecified):
            return self.handle_object(object.date)
        elif isinstance(object, Interval) or isinstance(object, Level1Interval) or isinstance(object, Level2Interval):
            return self.handle_interval(object)
        elif isinstance(object, LongYear) or isinstance(object, ExponentialYear):
            return self.handle_yearonly(object)
        elif isinstance(object, OneOfASet) or isinstance(object, MultipleDates):
            return self.handle_set(object)
        elif isinstance(object, str) or object is None:
            if object == "open":
                return SortableDateRange()
            else:
                dr = SortableDateRange()
                dr.lower = dr.lower_fuzzy = dr.upper = dr.upper_fuzzy = object
                return dr
        elif isinstance(object, list):
            if len(object) == 1:
                return self.handle_object(object[0])

        raise UnhandledEDTFException()

    def handle_date(self, date, fuzzy_padding=None):
        dr = SortableDateRange()
        # support for edtf.Date
        year = date._precise_year(EARLIEST)
        month = date._precise_month(EARLIEST)
        day = date._precise_day(EARLIEST)
        dr.lower = dr.lower_fuzzy = self.to_sortable_date(year=year, month=month, day=day)

        if fuzzy_padding:
            transposed_year = (year % 400) + 400
            lower_fuzzy = datetime.date(year=transposed_year, month=month, day=day) - fuzzy_padding
            year_diff = transposed_year - lower_fuzzy.year
            dr.lower_fuzzy = self.to_sortable_date(year=(year - year_diff), month=lower_fuzzy.month, day=lower_fuzzy.day)

        year = date._precise_year(LATEST)
        month = date._precise_month(LATEST)
        try:
            day = date._precise_day(LATEST)
        except ValueError:
            day = self.calculate_upper_day(year, month)
        dr.upper = dr.upper_fuzzy = self.to_sortable_date(year=year, month=month, day=day)

        if fuzzy_padding:
            transposed_year = (year % 400) + 400
            upper_fuzzy = datetime.date(year=transposed_year, month=month, day=day) + fuzzy_padding
            year_diff = upper_fuzzy.year - transposed_year
            fuzzy_year = year + year_diff
            day = upper_fuzzy.day

            # we need to recaculate the day under special circumstances
            if date.day is None and not self.is_season(date) and (date.precision == PRECISION_YEAR or date.precision == PRECISION_MONTH):
                day = self.calculate_upper_day(fuzzy_year, upper_fuzzy.month)
            elif date.day is not None and int(date.day) >= 29 and upper_fuzzy.month == 2:
                day = self.calculate_upper_day(fuzzy_year, upper_fuzzy.month)

            dr.upper_fuzzy = self.to_sortable_date(year=fuzzy_year, month=upper_fuzzy.month, day=day)

        return dr

    def calculate_upper_day(self, year, month):
        if month != 2:
            day = calendar.monthrange(1, month)[1]
        elif self.is_leap_year(year):
            day = 29
        else:
            day = 28

        return day

    def is_season(self, date):
        return hasattr(date, "season") and date.season is not None

    def handle_set(self, l):
        """Called to handle a list of dates"""
        arr = []
        for item in l.objects:
            arr.append(self.handle_object(item))

        return arr

    def handle_interval(self, object):
        dr = SortableDateRange()

        lower = self.handle_object(object.lower)
        dr.lower = lower.lower
        dr.lower_fuzzy = lower.lower_fuzzy

        upper = self.handle_object(object.upper)
        dr.upper = upper.upper
        dr.upper_fuzzy = upper.upper_fuzzy

        return dr

    def handle_yearonly(self, object):
        dr = SortableDateRange()
        try:
            # support for edtf.ExponentialYear
            num_length = len(str(object._precise_year()))
            sig_digits = str(object._precise_year())[0 : int(object.precision)]
            padding = num_length - int(object.precision)
            dr.lower = dr.lower_fuzzy = self.to_sortable_date(year=(sig_digits + ("0" * padding)))
            dr.upper = dr.upper_fuzzy = self.to_sortable_date(year=(sig_digits + ("9" * padding)), month=12, day=31)
        except:
            # support for edtf.LongYear
            dr.lower = dr.lower_fuzzy = self.to_sortable_date(year=object._precise_year())
            dr.upper = dr.upper_fuzzy = self.to_sortable_date(year=object._precise_year(), month=12, day=31)

        return dr

    def get_fuzzy_padding(self, object):
        padding_day_precision = relativedelta(days=self.fuzzy_day_padding).normalized()
        padding_month_precision = relativedelta(months=self.fuzzy_month_padding).normalized()
        padding_year_precision = relativedelta(years=self.fuzzy_year_padding).normalized()
        padding_season_precision = relativedelta(weeks=self.fuzzy_season_padding).normalized()

        if isinstance(object, UncertainOrApproximate):
            # from https://github.com/ixc/python-edtf/blob/master/edtf/parser/parser_classes.py#L366
            if not object.ua:
                return relativedelta(0)
            multiplier = object.ua._get_multiplier()

            if object.date.precision == PRECISION_DAY:
                result = multiplier * padding_day_precision
            elif object.date.precision == PRECISION_MONTH:
                result = multiplier * padding_month_precision
            elif object.date.precision == PRECISION_YEAR:
                result = multiplier * padding_year_precision
            return result

        elif isinstance(object, PartialUncertainOrApproximate):
            # from https://github.com/ixc/python-edtf/blob/master/edtf/parser/parser_classes.py#L528
            result = relativedelta(0)

            if object.year_ua:
                result += padding_year_precision * object.year_ua._get_multiplier()
            if object.month_ua:
                result += padding_month_precision * object.month_ua._get_multiplier()
            if object.day_ua:
                result += padding_day_precision * object.day_ua._get_multiplier()

            if object.year_month_ua:
                result += padding_year_precision * object.year_month_ua._get_multiplier()
                result += padding_month_precision * object.year_month_ua._get_multiplier()
            if object.month_day_ua:
                result += padding_day_precision * object.month_day_ua._get_multiplier()
                result += padding_month_precision * object.month_day_ua._get_multiplier()

            if object.season_ua:
                result += padding_season_precision * object.season_ua._get_multiplier()

            if object.all_ua:
                multiplier = object.all_ua._get_multiplier()

                if object.precision == PRECISION_DAY:
                    result += multiplier * padding_day_precision
                    result += multiplier * padding_month_precision
                    result += multiplier * padding_year_precision
                elif object.precision == PRECISION_MONTH:
                    result += multiplier * padding_month_precision
                    result += multiplier * padding_year_precision
                elif object.precision == PRECISION_YEAR:
                    result += multiplier * padding_year_precision

            return result

        return None


class UnhandledEDTFException(Exception):
    pass
