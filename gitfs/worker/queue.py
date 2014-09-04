from Queue import Queue


class BaseQueue(object):
    def __init__(self):
        self.queue = Queue()

    def commit(self, *args, **kwargs):
        raise NotImplemented()

    def get(self, *args, **kwargs):
        return self.queue.get(*args, **kwargs)


class MergeQueue(BaseQueue):

    def add(self, job):
        self.queue.put(job)

    def commit(self, add=None, message=None, remove=None):
        if message is None:
            raise ValueError("Message shoduld not be None")

        if add is None and remove is None:
            message = "You need to add or to remove some files from/to index"
            raise ValueError(message)

        self.queue.put({
            'type': 'commit',
            'params': {
                'add': self._to_list(add),
                'message': message,
                'remove': self._to_list(remove),
            }
        })

    def _to_list(self, variable):
        variable = variable or []

        if not isinstance(variable, list):
            variable = [variable]

        return variable
