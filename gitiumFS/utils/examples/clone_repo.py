from utils import Repository


path = 'path_to_repo'
remote_url = 'git@github.com:vtemian/testing'

repo = Repository.clone_repository(path, remote_url)
