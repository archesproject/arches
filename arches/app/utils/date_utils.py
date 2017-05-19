from flexidate import FlexiDate

class SortableDate(object):
    def __init__(self, date):
        self.orig_date = date
        self.fd = FlexiDate.from_str(str(self.orig_date))
        self.year = None
        self.month =  None
        self.day = None
        if self.fd is not None:
            self.year = self.fd.year
            self.month = '1' if self.fd.month == '0' or self.fd.month is '' else self.fd.month
            self.day = '1' if self.fd.day == '0' or self.fd.day is '' else self.fd.day

    def as_float(self):
        try:
            year = int(self.year) * 10000
            month = self.month.zfill(2)
            day = self.day.zfill(2)
            #return int("%s%s%s" % (self.year,month,day))
            return year + int("%s%s" % (month,day))
        except:
            return None

    def is_valid(self):
        return False if self.as_float() is None else True