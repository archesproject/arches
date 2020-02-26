"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import sys
from tests.base_test import ArchesTestCase
from arches.app.utils.date_utils import ExtendedDateFormat

# these tests can be run from the command line via
# python manage.py test tests/utils/date_utils_tests.py --pattern="*.py" --settings="tests.test_settings"

EDTF_DATES = (
    # ******************************* LEVEL 0 *********************************
    # year, month, day
    ("2001-02-03", "20010203"),
    # year, month
    ("2008-12", "20081201", "20081231"),
    # year
    ("2008", "20080101", "20081231"),
    # a negative year
    ("-0999", "-9989899", "-9988769"),
    # year zero
    ("0000", "101", "1231"),
    # DateTimes
    ("2001-02-03T09:30:01", "20010203"),
    ("2004-01-01T10:10:10Z", "20040101"),
    ("2004-01-01T10:10:10+05:00", "20040101"),
    # An interval beginning sometime in 1964 and ending sometime in 2008. Year precision.
    ("1964/2008", "19640101", "20081231"),
    # An interval beginning sometime in June 2004 and ending sometime in August of 2006. Month precision.
    ("2004-06/2006-08", "20040601", "20060831"),
    # An interval beginning sometime on February 1, 2004 and ending sometime on February 8, 2005. Day precision.
    ("2004-02-01/2005-02-08", "20040201", "20050208"),
    # An interval beginning sometime on February 1, 2004 and ending sometime in February 2005. The precision of the interval is not defined; the start endpoint has day precision and the end endpoint has month precision.
    ("2004-02-01/2005-02", "20040201", "20050228"),
    # An interval beginning sometime on February 1, 2004 and ending sometime in 2005. The start endpoint has day precision and the end endpoint has year precision.
    ("2004-02-01/2005", "20040201", "20051231"),
    # An interval beginning sometime in 2005 and ending sometime in February 2006.
    ("2005/2006-02", "20050101", "20060228"),
    # ******************************* LEVEL 1 *********************************
    # Uncertain/Approximate
    # uncertain: possibly the year 1984, but not definitely
    ("1984?", "19840101", "19841231", "19830101", "19851231"),
    ("2004-06-11?", "20040611", "20040611", "20040610", "20040612"),
    ("2004-06?", "20040601", "20040630", "20040501", "20040731"),
    # "approximately" the year 1984
    ("1984~", "19840101", "19841231", "19830101", "19851231"),
    # the year is approximately 1984 and even that is uncertain
    ("1984?~", "19840101", "19841231", "19820101", "19861231"),
    # Unspecified
    # some unspecified year in the 1990s.
    ("199u", "19900101", "19991231"),
    # some unspecified year in the 1900s.
    ("19uu", "19000101", "19991231"),
    # some month in 1999
    ("1999-uu", "19990101", "19991231"),
    # some day in January 1999
    ("1999-01-uu", "19990101", "19990131"),
    # some day in 1999
    ("1999-uu-uu", "19990101", "19991231"),
    # L1 Extended Interval
    # beginning unknown, end 2006
    ("unknown/2006", "unknown", "20061231"),
    # beginning June 1, 2004, end unknown
    ("2004-06-01/unknown", "20040601", "unknown"),
    # beginning January 1 2004 with no end date
    ("2004-01-01/open", "20040101", "None"),
    # interval beginning approximately 1984 and ending June 2004
    ("1984~/2004-06", "19840101", "20040630", "19830101", "20040630"),
    # interval beginning 1984 and ending approximately June 2004
    ("1984/2004-06~", "19840101", "20040630", "19840101", "20040731"),
    ("1984?/2004?~", "19840101", "20041231", "19830101", "20061231"),
    ("1984~/2004~", "19840101", "20041231", "19830101", "20051231"),
    # interval whose beginning is uncertain but thought to be 1984, and whose end is uncertain and approximate but thought to be 2004
    ("1984-06?/2004-08?", "19840601", "20040831", "19840501", "20040930"),
    ("1984-06-02?/2004-08-08~", "19840602", "20040808", "19840601", "20040809"),
    ("1984-06-02?/unknown", "19840602", "unknown", "19840601", "unknown"),
    # Year exceeding 4 digits
    # the year 170000002
    ("y170000002", "1700000020101", "1700000021231"),
    # the year -170000002
    ("y-170000002", "-1700000019899", "-1700000018769"),
    # Seasons
    # Spring, 2001
    ("2001-21", "20010301", "20010531"),
    # Summer, 2003
    ("2003-22", "20030601", "20030831"),
    # Autumn, 2000
    ("2000-23", "20000901", "20001130"),
    # Winter, 2010
    ("2010-24", "20101201", "20101231"),
    # ******************************* LEVEL 2 *********************************
    # Partial Uncertain/ Approximate
    # uncertain year; month, day known
    ("2004?-06-11", "20040611", "20030611", "20050611"),
    # year and month are approximate; day known
    ("2004-06~-11", "20040611", "20030511", "20050711"),
    # uncertain month, year and day known
    ("2004-(06)?-11", "20040611", "20040511", "20040711"),
    # day is approximate; year, month known
    ("2004-06-(11)~", "20040611", "20040610", "20040612"),
    # Year known, month within year is approximate and uncertain
    ("2004-(06)?~", "20040601", "20040630", "20040401", "20040831"),
    # Year known, month and day uncertain
    ("2004-(06-11)?", "20040611", "20040510", "20040712"),
    # Year uncertain, month known, day approximate
    ("2004?-06-(11)~", "20040611", "20030610", "20050612"),
    # Year uncertain and month is both uncertain and approximate
    ("(2004-(06)~)?", "20040601", "20040630", "20030401", "20050831"),
    # This has the same meaning as the previous example.
    ("2004?-(06)?~", "20040601", "20040630", "20030401", "20050831"),
    # Year uncertain, month and day approximate.
    (("(2004)?-06-04~", "2004?-06-04~"), "20040604", "20030503", "20050705"),
    # Year known, month and day approximate. Note that this has the same meaning as the following.
    (("(2011)-06-04~", "2011-(06-04)~"), "20110604", "20110503", "20110705"),
    # Year known, month and day approximate.
    ("2011-(06-04)~", "20110604", "20110503", "20110705"),
    # Approximate season (around Autumn 2011)
    ("2011-23~", "20110901", "20111130", "20110609", "20120222"),
    # Years wrapping
    ("2011-24~", "20111201", "20111231", "20110908", "20120324"),
    # Partial unspecified
    # December 25 sometime during the 1560s
    ("156u-12-25", "15601225", "15691225"),
    # December 25 sometime during the 1500s
    ("15uu-12-25", "15001225", "15991225"),
    # Year and day of month specified, month unspecified
    ("1560-uu-25", "15600125", "15601225"),
    ("15uu-12-uu", "15001201", "15991231"),
    # One of a Set
    # One of the years 1667, 1668, 1670, 1671, 1672
    ("[1667,1668, 1670..1672]", [["16670101", "16671231"], ["16680101", "16681231"], ["16700101", "16721231"]]),
    # December 3, 1760 or some earlier date
    ("[..1760-12-03]", [["None", "17601203"]]),
    # December 1760 or some later month
    ("[1760-12..]", [["17601201", "None"]]),
    # January or February of 1760 or December 1760 or some later month
    ("[1760-01, 1760-02, 1760-12..]", [["17600101", "17600131"], ["17600201", "17600229"], ["17601201", "None"]]),
    # Either the year 1667 or the month December of 1760.
    ("[1667, 1760-12]", [["16670101", "16671231"], ["17601201", "17601231"]]),
    # Multiple Dates
    # All of the years 1667, 1668, 1670, 1671, 1672
    ("{1667,1668, 1670..1672}", [["16670101", "16671231"], ["16680101", "16681231"], ["16700101", "16721231"]]),
    # The year 1960 and the month December of 1961.
    ("{1960, 1961-12}", [["19600101", "19601231"], ["19611201", "19611231"]]),
    # Masked Precision
    # A date during the 1960s
    ("196x", "19600101", "19691231"),
    # A date during the 1900s
    ("19xx", "19000101", "19991231"),
    # L2 Extended Interval
    # An interval in June 2004 beginning approximately the first and ending approximately the 20th.
    ("2004-06-(01)~/2004-06-(20)~", "20040601", "20040620", "20040531", "20040621"),
    # The interval began on an unspecified day in June 2004.
    ("2004-06-uu/2004-07-03", "20040601", "20040703"),
    # Year Requiring More than Four Digits - Exponential Form
    # the year 170000000
    ("y17e7", "1700000000101", "1700000001231"),
    # # the year -170000000
    ("y-17e7", "-1699999999899", "-1699999998769"),
    # # Some year between 171010000 and 171999999, estimated to be 171010000 ('p3' indicates a precision of 3 significant digits.)
    ("y17101e4p3", "1710000000101", "1719999991231"),
)

NEGATIVE_DATES = (
    # ******************************* LEVEL 1 *********************************
    # Uncertain/Approximate
    ("-1984?", "-19839899", "-19838769", "-19849899", "-19828769"),
    ("-2004-06-11?", "-20039389", "-20039389", "-20039390", "-20039388"),
    ("-2004-06?", "-20039399", "-20039370", "-20039499", "-20039269"),
    ("-1295~", "-12949899", "-12948769", "-12959899", "-12938769"),
    ("-1295?~", "-12949899", "-12948769", "-12969899", "-12928769"),
    ("-0095?~", "-949899", "-948769", "-969899", "-928769"),
    ("-1550~/-1295~", "-15499899", "-12948769", "-15509899", "-12938769"),
)

LEAP_YEARS = (
    # ******************************* LEVEL 1 *********************************
    # Uncertain/Approximate
    # known year, uncertain month
    ("2000-01?", "20000101", "20000131", "19991201", "20000229"),
    ("2001-01?", "20010101", "20010131", "20001201", "20010228"),
    # uncertain month, year and day known
    ("2000-(01)?-30", "20000130", "20000130", "19991230", "20000229"),
)

NON_EDTF_DATES = (
    # test long year
    ("975845000", "9758450000101", "9758450001231"),
    # test unpadded year 0
    ("0", "101", "1231"),
    # test unpadded year
    ("34", "340101", "341231"),
    # test null value
    ("", "None", "None"),
)

INVALID_EDTF_DATES = (
    # test long year
    ("al;ksdjf",),
)


class SortableDateTests(ArchesTestCase):
    def parse(self, test_case):
        i = test_case[0]
        if isinstance(i, tuple):
            i, o = i
        else:
            o = i

        print("parsing '%s'" % i)
        f = ExtendedDateFormat(i)

        if len(test_case) == 2:
            if f.result_set:
                for i, item in enumerate(f.result_set):
                    self.assertEqual(str(item.lower), test_case[1][i][0])
                    self.assertEqual(str(item.upper), test_case[1][i][1])
            else:
                self.assertEqual(str(f.lower), test_case[1])
        elif len(test_case) == 3:
            self.assertEqual(str(f.lower), test_case[1])
            self.assertEqual(str(f.upper), test_case[2])
        elif len(test_case) == 4:
            self.assertEqual(str(f.lower), test_case[1])
            self.assertEqual(str(f.upper), test_case[1])
            self.assertEqual(str(f.lower_fuzzy), test_case[2])
            self.assertEqual(str(f.upper_fuzzy), test_case[3])
        elif len(test_case) == 5:
            self.assertEqual(str(f.lower), test_case[1])
            self.assertEqual(str(f.upper), test_case[2])
            self.assertEqual(str(f.lower_fuzzy), test_case[3])
            self.assertEqual(str(f.upper_fuzzy), test_case[4])
        elif len(test_case) == 1:
            self.assertEqual(f.is_valid(), False)
        else:
            raise Exception(test_case)

    def test_edtf_parsing(self):
        for test_case in EDTF_DATES:
            self.parse(test_case)

    def test_negative_date_parsing(self):
        for test_case in NEGATIVE_DATES:
            self.parse(test_case)

    def test_leap_year_parsing(self):
        for test_case in LEAP_YEARS:
            self.parse(test_case)

    def test_non_edtf_parsing(self):
        for test_case in NON_EDTF_DATES:
            self.parse(test_case)

    def test_invalid_edtf_parsing(self):
        for test_case in INVALID_EDTF_DATES:
            self.parse(test_case)
