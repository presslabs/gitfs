import threading


lock = threading.RLock()


def with_lock(f):
    def decorated(*args, **kwargs):
        with lock:
            result = f(*args, **kwargs)
        return result
    return decorated
