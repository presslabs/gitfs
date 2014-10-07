from threading import Thread


class Peasant(Thread):
    def __init__(self, *args, **kwargs):
        super(Peasant, self).__init__()

        for name, value in kwargs.iteritems():
            setattr(self, name, value)
