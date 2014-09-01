import time


class retry(object):
    def __init__(self, each=3, times=None):
        self.each = each
        self.times = times or True

    def __call__(self, f):
        def decorated(*args, **kwargs):
            while self.times:
                try:
                    return f(*args, **kwargs)
                except:
                    time.sleep(self.each)

                if isinstance(self.times, int):
                    self.times -= 1

        return decorated
