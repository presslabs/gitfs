import time
import threading
from functools import wraps


class retry(object):
    def __init__(self, each=3, times=None):
        self.each = each
        self.times = times or True

    def __call__(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            while self.times:
                try:
                    return f(*args, **kwargs)
                except:
                    time.sleep(self.each)

                if isinstance(self.times, int):
                    self.times -= 1

        return decorated


class while_not(object):
    def __init__(self, event_name, retry=0.2):
        self.event_name = event_name
        self.retry = retry

    def __call__(self, f):
        @wraps(f)
        def decorated(obj, *args, **kwargs):
            event = getattr(obj, self.event_name, None)
            if not event:
                raise ValueError("Except that %s to have %s" %
                                 (obj.__class__.__name__, self.event_name))
            if not isinstance(event, threading._Event):
                raise TypeError("%s should be of type threading.Event" %
                                self.event_name)
            while event.is_set():
                print "Wait to %s" % f.__name__
                time.sleep(self.retry)

            return f(obj, *args, **kwargs)

        return decorated
