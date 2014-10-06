import time
import threading
from functools import wraps


class while_not(object):
    def __init__(self, event, wait=0.2):
        self.event = event
        self.wait = wait

    def __call__(self, f):
        @wraps(f)
        def decorated(obj, *args, **kwargs):
            if not self.event:
                raise ValueError("Except that %s to not be None %s" %
                                 obj.__class__.__name__)
            if not isinstance(self.event, threading._Event):
                raise TypeError("%s should be of type threading.Event" %
                                self.event)

            while self.event.is_set():
                print "wait"
                time.sleep(self.wait)

            return f(obj, *args, **kwargs)

        return decorated
