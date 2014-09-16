from threading import Event

import pytest
from mock import MagicMock, patch, call

from gitfs.utils.decorators import retry, while_not


class MockedWraps(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, f):
        def decorated(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated


class EmptyMock(object):
    def __init__(self, **kwargs):
        for name, value in kwargs.iteritems():
            setattr(self, name, value)


class TestRetryDecorator(object):
    def test_retry(self):
        mocked_time = MagicMock()
        mocked_method = MagicMock(side_effect=ValueError)

        with patch.multiple('gitfs.utils.decorators', wraps=MockedWraps,
                            time=mocked_time):
            again = retry(times=3)

            with pytest.raises(ValueError):
                again(mocked_method)("arg", kwarg="kwarg")

            mocked_time.sleep.has_calls([call(3), call(3), call(1)])
            mocked_method.has_calls([call("arg", kwarg="kwarg")])


class TestWhileNotDecorator(object):
    def test_while_not_with_missing_event(self):
        mocked_method = MagicMock()
        mocked_self = EmptyMock()

        with patch.multiple('gitfs.utils.decorators', wraps=MockedWraps):
            with pytest.raises(ValueError):
                not_now = while_not("obj")
                not_now(mocked_method)(mocked_self, "arg", kwarg="kwarg")

    def test_while_not_with_invalid_event_type(self):
        mocked_method = MagicMock()
        mocked_self = EmptyMock(obj="obj")

        with patch.multiple('gitfs.utils.decorators', wraps=MockedWraps):
            with pytest.raises(TypeError):
                not_now = while_not("obj")
                not_now(mocked_method)(mocked_self, "arg", kwarg="kwarg")

    def test_while_not(self):
        an_event = Event()
        an_event.set()

        mocked_method = MagicMock()
        mocked_time = MagicMock()
        mocked_self = EmptyMock(obj=an_event)

        mocked_time.sleep.side_effect = lambda x: an_event.clear()
        mocked_method.__name__ = "name"

        with patch.multiple('gitfs.utils.decorators', wraps=MockedWraps,
                            time=mocked_time):
            not_now = while_not("obj")
            not_now(mocked_method)(mocked_self, "arg", kwarg="kwarg")

            mocked_time.sleep.assert_called_once_with(0.2)
