import threading


want_to_merge = threading.Event()
read_only = threading.Event()
somebody_is_writing = threading.Event()
merging = threading.Event()
fetching = threading.Event()
pushing = threading.Event()
