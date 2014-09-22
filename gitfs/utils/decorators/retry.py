import time
from functools import wraps


class retry(object):
    def __init__(self, each=3, times=True):
        self.each = each
        self.times = times

    def __call__(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            while self.times:
                try:
                    return f(*args, **kwargs)
                except:
                    time.sleep(self.each)

                if (isinstance(self.times, int) and not
                   isinstance(self.times, bool)):
                    self.times -= 1

            return f(*args, **kwargs)

        return decorated
