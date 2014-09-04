import time

from gitfs.worker.peasant import Peasant


class FetchWorker(Peasant):
    def run(self):
        while True:
            time.sleep(self.timeout)
            self.repository.fetch(self.upstream, self.branch)

            if not self.want_to_merge.is_set():
                self.want_to_merge.set()
            elif not self.somebody_is_writing.is_set():
                self.merge()

    def fetch(self):
        try:
            self.read_only.clear()
            self.repository.fetch(self.upstream, self.branch)
        except:
            self.read_only.set()
