class CommitsList(object):
    def __init__(self, commits=None, hashes=None):
        self.commits = commits or []
        self.hashes = hashes or []

    def __contains__(self, commit):
        return commit.hex in self.hashes

    def index(self, commit):
        return self.hashes.index(commit.hex)

    def __getitem__(self, val):
        commits = self.commits[val]
        hashes = self.hashes[val]
        return CommitsList(commits, hashes)

    def __iter__(self):
        return self.commits.__iter__()

    def append(self, commit):
        self.commits.append(commit)
        self.hashes.append(commit.hex)

    def __repr__(self):
        return self.commits.__repr__()

    def __len__(self):
        return len(self.commits)
