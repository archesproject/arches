import calendar
from edtf import parse_edtf
from edtf.parser.parser_classes import Date, DateAndTime, Interval, Unspecified, \
    UncertainOrApproximate, Level1Interval, LongYear, Season, \
    PartialUncertainOrApproximate, PartialUnspecified, OneOfASet, \
    MultipleDates, Level2Interval, ExponentialYear

# class SortableDate(object):
#     def __init__(self, date):
#         self.orig_date = date
#         self.fd = FlexiDate.from_str(str(self.orig_date))
#         self.year = None
#         self.month =  None
#         self.day = None
#         if self.fd is not None:
#             self.year = self.fd.year
#             self.month = '1' if self.fd.month == '0' or self.fd.month is '' else self.fd.month
#             self.day = '1' if self.fd.day == '0' or self.fd.day is '' else self.fd.day

#     def as_float(self):
#         try:
#             year = int(self.year) * 10000
#             month = self.month.zfill(2)
#             day = self.day.zfill(2)
#             #return int("%s%s%s" % (self.year,month,day))
#             return year + int("%s%s" % (month,day))
#         except:
#             return None

#     def is_valid(self):
#         return False if self.as_float() is None else True
    
class SortableDateRange(object):
    def __init__(self):
        self.lower = None
        self.upper = None

class ExtendedDateFormat(SortableDateRange):
    def __init__(self, date=None):
        super(ExtendedDateFormat, self).__init__()
        self.orig_date = None
        self.edtf = None
        self.result_set = None
        self.sortable_date = None
        
        self.parse(date)

    def parse(self, date=None):
        if date == None:
            return None

        self.edtf = None
        self.orig_date = date
        self.result_set = None

        try: 
            # handle for incorrectly formatted year only dates 
            # (eg: 290 => 0290, 11909 => y11909)
            if int(date) >= 0: 
                date = str(int(date)).zfill(4)
            else:
                date = str(int(date)).zfill(5)
            if len(str(abs(int(date)))) > 4 and int(date) != 0:
                date = 'y' + date
        except:
            pass

        self.edtf = parse_edtf(date)
         
        result = self.handle_object(self.edtf)
        if isinstance(result, list):
            self.result_set = result
        else:
            self.lower, self.upper = result

    def is_valid(self):
        return True if self.lower or self.upper or self.result_set else False

    def is_leap_year(self, year):
        if ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0):
            return True
        return False

    def to_sortable_date(self, **kwargs):
        year = kwargs.pop('year', None)
        month = kwargs.pop('month', '')
        month = '1' if month == '0' or month is '' else month
        day = kwargs.pop('day', '')
        day = '1' if day == '0' or day is '' else day
        try:
            year = int(year) * 10000
            month = str(month).zfill(2)
            day = str(day).zfill(2)
            #return int("%s%s%s" % (self.year,month,day))
            return year + int("%s%s" % (month,day))
        except:
            return None

    def handle_object(self, object):
        """ 
        Called to handle any date type, looks for the correct handling 

        """

        # print type(object)
        # print object
        if (isinstance(object, Date) or
            isinstance(object, Unspecified) or
            isinstance(object, Season) or
            isinstance(object, PartialUncertainOrApproximate) or
            isinstance(object, PartialUnspecified)):
            return self.handle_date(object)
        elif (isinstance(object, DateAndTime) or
              isinstance(object, UncertainOrApproximate)):
            return self.handle_object(object.date)
        elif (isinstance(object, Interval) or
              isinstance(object, Level1Interval) or
              isinstance(object, Level2Interval)):
            return self.handle_interval(object)
        elif (isinstance(object, LongYear) or 
              isinstance(object, ExponentialYear)):
            return self.handle_yearonly(object)
        elif (isinstance(object, OneOfASet) or
              isinstance(object, MultipleDates)):
            return self.handle_set(object)
        elif (isinstance(object, basestring) or
              object is None):
            if object == 'open':
                return (None,None)
            else:
                return (object,object)
        else:
            raise Exception('')

    def handle_date(self, date):
        # support for edtf.Date
        year = date._precise_year('earliest')
        month = date._precise_month('earliest')
        day = date._precise_day('earliest')
        lower = self.to_sortable_date(year=year, month=month, day=day)

        year = date._precise_year('latest')
        month = date._precise_month('latest')
        try:
            day = date._precise_day('latest')
        except ValueError:
            if month != 2:
                day = calendar.monthrange(1, month)[1]
            elif is_leap_year(year):
                day = 29
            else:
                day = 28
        upper = self.to_sortable_date(year=year, month=month, day=day)

        return (lower,upper)

    def handle_set(self, l):
        """Called to handle a list of dates"""
        arr = []
        for item in l.objects:
            dr = SortableDateRange()
            dr.lower, dr.upper = self.handle_object(item)
            arr.append(dr)

        return arr

    def handle_interval(self, object):
        lower = self.handle_object(object.lower)[0]
        upper = self.handle_object(object.upper)[1]
        return (lower, upper)

    def handle_yearonly(self, object):
        try:
            # support for edtf.ExponentialYear
            num_length = len(str(object._precise_year()))
            sig_digits = str(object._precise_year())[0:int(object.precision)]
            padding = num_length - int(object.precision)
            lower = self.to_sortable_date(year=(sig_digits + ('0' * padding)))
            upper = self.to_sortable_date(year=(sig_digits + ('9' * padding)), month=12, day=31)
        except:
            # support for edtf.LongYear
            lower = self.to_sortable_date(year=object._precise_year())
            upper = self.to_sortable_date(year=object._precise_year(), month=12, day=31)
        return (lower, upper)
