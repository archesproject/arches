from flexidate import FlexiDate

class SortableDate(object):
    def __init__(self, date):
        fd = FlexiDate.from_str(str(date))
        self.year = fd.year
        self.month = '1' if fd.month == '0' or fd.month is '' else fd.month
        self.day = '1' if fd.day == '0' or fd.day is '' else fd.day

    def as_float(self):
        year = int(self.year) * 10000
        month = self.month.zfill(2)
        day = self.day.zfill(2)
        #return int("%s%s%s" % (self.year,month,day))
        return year + int("%s%s" % (month,day))
