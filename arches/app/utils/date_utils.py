from flexidate import FlexiDate

class SortableDate(object):
    def __init__(self, date):
        fd = FlexiDate.from_str(str(date))
        self.year = fd.year
        self.month = fd.month
        self.day = fd.day

    def as_float(self):
        year = int(self.year) * 10000
        month = self.month.zfill(2)
        day = self.day.zfill(2)
        #return int("%s%s%s" % (self.year,month,day))
        return year + int("%s%s" % (month,day))
