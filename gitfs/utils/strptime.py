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
    "%a": "(?P<weekday>[a-z]+)",
    "%A": "(?P<weekday>[a-z]+)",
    "%b": "(?P<month>[a-z]+)",
    "%B": "(?P<month>[a-z]+)",
    "%C": "(?P<century>\d\d?)",
    "%d": "(?P<day>\d\d?)",
    "%D": "(?P<month>\d\d?)/(?P<day>\d\d?)/(?P<year>\d\d)",
    "%e": "(?P<day>\d\d?)",
    "%h": "(?P<month>[a-z]+)",
    "%H": "(?P<hour>\d\d?)",
    "%I": "(?P<hour12>\d\d?)",
    "%j": "(?P<yearday>\d\d?\d?)",
    "%m": "(?P<month>\d\d?)",
    "%M": "(?P<minute>\d\d?)",
    "%p": "(?P<ampm12>am|pm)",
    "%R": "(?P<hour>\d\d?):(?P<minute>\d\d?)",
    "%S": "(?P<second>\d\d?)",
    "%T": "(?P<hour>\d\d?):(?P<minute>\d\d?):(?P<second>\d\d?)",
    "%U": "(?P<week>\d\d)",
    "%w": "(?P<weekday>\d)",
    "%W": "(?P<weekday>\d\d)",
    "%y": "(?P<year>\d\d)",
    "%Y": "(?P<year>\d\d\d\d)",
    "%%": "%"
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
        y = get("year")
        if y:
            y = int(y)
            if y < 68:
                y = 2000 + y
            elif y < 100:
                y = 1900 + y
            tm[0] = y

        # extract month
        m = get("month")
        if m:
            if m in MONTHS:
                m = MONTHS.index(m) + 1
            tm[1] = int(m)

        # extract day
        d = get("day")
        if d:
            tm[2] = int(d)

        # extract time elements
        h = get("hour")
        if h:
            tm[3] = int(h)
        else:
            h = get("hour12")
            if h:
                h = int(h)
                if string.lower(get("ampm12", "")) == "pm":
                    h = h + 12
                tm[3] = h
        m = get("minute")
        if m:
            tm[4] = int(m)
        s = get("second")
        if s:
            tm[5] = int(s)

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
