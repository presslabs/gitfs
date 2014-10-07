class Merger(object):
    def __init__(self, repository, **kwargs):
        self.repository = repository
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])
