import pytest
import datetime as dt

from gitfs.utils import strptime


class TestDateTimeUtils(object):

    def test_strptime(self):
        date = dt.date(2014, 8, 21)
        datetime = dt.datetime(2014, 8, 21, 1, 2, 3)
        assert strptime("2014-08-21 01:02:03", "%Y-%m-%d %H:%M:%S") == date
        assert strptime("2014-08-21 01:02:03", "%Y-%m-%d %H:%M:%S", to_datetime=True) == datetime


        date = dt.date(2014, 8, 30)
        datetime = dt.datetime(2014, 8, 30, 1, 2, 3)
        assert strptime("30 Aug 14 01:02:03", "%d %b %y %H:%M:%S") == date
        assert strptime("30 Aug 14 01:02:03", "%d %b %y %H:%M:%S", to_datetime=True) == datetime

        date = dt.date(1970, 1, 1)
        datetime = dt.datetime(1970, 1, 1, 13, 30)
        assert strptime("1 Jan 70 1:30pm", "%d %b %y %I:%M%p") == date
        assert strptime("1 Jan 70 1:30pm", "%d %b %y %I:%M%p", to_datetime=True) == datetime

        with pytest.raises(ValueError):
            strptime("31 Nov 14 01:02:03", "%d %b %y %H:%M:%S")
