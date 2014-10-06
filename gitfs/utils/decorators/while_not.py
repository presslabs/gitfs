import threading
from functools import wraps


class while_not(object):
    def __init__(self, event):
        self.event = event

    def __call__(self, f):
        @wraps(f)
        def decorated(obj, *args, **kwargs):
            if not self.event:
                raise ValueError("Except that %s to not be None %s" %
                                 obj.__class__.__name__)
            if not isinstance(self.event, threading._Event):
                raise TypeError("%s should be of type threading.Event" %
                                self.event)
            self.event.wait()
            return f(obj, *args, **kwargs)

        return decorated
