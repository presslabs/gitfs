from threading import Thread, Event


class Peasant(Thread):
    def __init__(self, *args, **kwargs):
        super(Peasant, self).__init__()

        for name, value in kwargs.iteritems():
            setattr(self, name, value)

        self.__stopped = Event()

    def stop(self):
        self.__stopped.set()

    @property
    def stopped(self):
        return self.__stopped.isSet()
