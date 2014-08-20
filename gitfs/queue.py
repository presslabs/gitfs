from ABC import ABCMeta, abstractmethod


class Queue(object):
    __metaclass__ = ABCMeta

    def __init__(self, queue):
        self.queue = queue

    @abstractmethod
    def __calll__(self, *args, **kwargs):
        raise NotImplemented()


class CommitQueue(Queue):
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
