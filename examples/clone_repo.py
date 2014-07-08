from gitiumFS.utils import Repository


path = 'path_to_repo'
remote_url = 'git://github.com/vtemian/testing'

repo = Repository.clone(remote_url, path)
