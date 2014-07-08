from gitiumFS.utils import Repository


path = 'path_to_repo'
repo = Repository(path)

file_path = "%s/README.md" % path
with open(file_path, 'w') as f:
  f.write("some content here")

repo.index.add("README.md")
repo.commit("my awesome message", "vlad", "vladtemian@gmail.com")

repo.push("origin", "master")
