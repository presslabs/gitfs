class View(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        for attr in kwargs:
            setattr(self, attr, kwargs[attr])
