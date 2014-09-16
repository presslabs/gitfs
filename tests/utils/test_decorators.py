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
    pass


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
