from gitiumFS.utils import Repository


path = 'path_to_repo'
repo = Repository(path)

repo.pull("origin", "master")
