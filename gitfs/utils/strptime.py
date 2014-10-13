# Copyright 2014 PressLabs SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import datetime
import re
import string

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
          "Sep", "Oct", "Nov", "Dec"]

SPEC = {
    # map formatting code to a regular expression fragment
    "%a": r"(?P<weekday>[a-z]+)",
    "%A": r"(?P<weekday>[a-z]+)",
    "%b": r"(?P<month>[a-z]+)",
    "%B": r"(?P<month>[a-z]+)",
    "%C": r"(?P<century>\d\d?)",
    "%d": r"(?P<day>\d\d?)",
    "%D": r"(?P<month>\d\d?)/(?P<day>\d\d?)/(?P<year>\d\d)",
    "%e": r"(?P<day>\d\d?)",
    "%h": r"(?P<month>[a-z]+)",
    "%H": r"(?P<hour>\d\d?)",
    "%I": r"(?P<hour12>\d\d?)",
    "%j": r"(?P<yearday>\d\d?\d?)",
    "%m": r"(?P<month>\d\d?)",
    "%M": r"(?P<minute>\d\d?)",
    "%p": r"(?P<ampm12>am|pm)",
    "%R": r"(?P<hour>\d\d?):(?P<minute>\d\d?)",
    "%S": r"(?P<second>\d\d?)",
    "%T": r"(?P<hour>\d\d?):(?P<minute>\d\d?):(?P<second>\d\d?)",
    "%U": r"(?P<week>\d\d)",
    "%w": r"(?P<weekday>\d)",
    "%W": r"(?P<weekday>\d\d)",
    "%y": r"(?P<year>\d\d)",
    "%Y": r"(?P<year>\d\d\d\d)",
    "%%": r"%"
}


class TimeParser(object):
    def __init__(self, format):
        # convert strptime format string to regular expression
        format = string.join(re.split("(?:\s|%t|%n)+", format))
        pattern = []

        try:
            for spec in re.findall("%\w|%%|.", format):
                if spec[0] == "%":
                    spec = SPEC[spec]
                pattern.append(spec)
        except KeyError:
            raise ValueError("unknown specificer: %s" % spec)

        self.pattern = re.compile("(?i)" + string.join(pattern, ""))

    def match(self, daytime):
        # match time string
        match = self.pattern.match(daytime)
        if not match:
            raise ValueError("format mismatch")
        get = match.groupdict().get

        tm = [0] * 9

        # extract year
        year = get("year")
        if year:
            year = int(year)
            if year < 68:
                year = 2000 + year
            elif year < 100:
                year = 1900 + year
            tm[0] = year

        # extract month
        month = get("month")
        if month:
            if month in MONTHS:
                month = MONTHS.index(month) + 1
            tm[1] = int(month)

        # extract day
        day = get("day")
        if day:
            tm[2] = int(day)

        # extract time elements
        hour = get("hour")
        if hour:
            tm[3] = int(hour)
        else:
            hour = get("hour12")
            if hour:
                hour = int(hour)
                if string.lower(get("ampm12", "")) == "pm":
                    hour = hour + 12
                tm[3] = hour

        minute = get("minute")
        if minute:
            tm[4] = int(minute)

        second = get("second")
        if second:
            tm[5] = int(second)

        # ignore weekday/yearday for now
        return tuple(tm)


def strptime(string, format="%a %b %d %H:%M:%S %Y", to_datetime=False):
    date = TimeParser(format).match(string)
    result = datetime.date(date[0], date[1], date[2])

    if to_datetime and len(date) > 3:
        time = datetime.time(date[3], date[4], date[5])
        result = datetime.datetime.combine(result, time)
        result = result.replace(tzinfo=None)

    return result
