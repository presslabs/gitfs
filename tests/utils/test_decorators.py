import pytest
from mock import MagicMock, patch, call

from gitfs.utils.decorators import retry


class MockedWraps(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, f):
        def decorated(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated


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
