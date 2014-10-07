import threading

from gitfs.utils.atomic import AtomicLong


syncing = threading.Event()
sync_done = threading.Event()

push_successful = threading.Event()
push_successful.set()

fetch_successful = threading.Event()
fetch_successful.set()

read_only = threading.Event()
fetch = threading.Event()
shutting_down = threading.Event()

writers = AtomicLong(0)

remote_operation = threading.Lock()
