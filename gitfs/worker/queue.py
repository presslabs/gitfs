from Queue import Queue


class BaseQueue(object):
    def __init__(self):
        self.queue = Queue()

    def __calll__(self, *args, **kwargs):
        raise NotImplemented()

    def get(self, *args, **kwargs):
        return self.queue.get(*args, **kwargs)


class CommitQueue(BaseQueue):
    def __call__(self, add=None, message=None, remove=None):
        if message is None:
            raise ValueError("Message shoduld not be None")

        if add is None and remove is None:
            message = "You need to add or to remove some files from/to index"
            raise ValueError(message)

        self.queue.put({
            'job_type': 'commit',
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


class PushQueue(BaseQueue):
    def __call__(self, message=None):
        if message is None:
            raise ValueError("Invalid push job")

        self.queue.put({
            'job_type': 'push',
            'params': {
                'message': message,
            }
        })
