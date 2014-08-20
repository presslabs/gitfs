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
        print 'commit queue was called'
        if message is None:
            raise ValueError("Message shoduld not be None")

        if add is None and remove is None:
            message = "You need to add or to remove some files from/to index"
            raise ValueError(message)

        add = add or []
        remove = remove or []

        if not isinstance(add, list):
            add = [add]

        if not isinstance(remove, list):
            remove = [remove]

        self.queue.put({
            'job_type': 'commit',
            'params': {
                'add': add,
                'message': message,
                'remove': remove,
            }
        })


class PushQueue(BaseQueue):
    def __call__(self, message=None):
        print "push queue was called", self.queue
        if message is None:
            raise ValueError("Invalid push job")

        self.queue.put({
            'job_type': 'push',
            'params': {
                'message': message,
            }
        })
