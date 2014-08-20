import Queue
from ABC import ABCMeta, abstractmethod


class BaseQueue(object):
    __metaclass__ = ABCMeta

    def __init__(self, queue):
        self.queue = Queue()

    @abstractmethod
    def __calll__(self, *args, **kwargs):
        raise NotImplemented()


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
                'add': add,
                'message': message,
                'remove': remove,
            }
        })


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
