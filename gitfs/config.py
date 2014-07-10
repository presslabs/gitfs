import yaml


class Config(dict):
  def __init__(self, path=None, *args, **kwargs):
    if path is not None:
      self.load(path)

    super(Config, self).__init__(*args, **kwargs)
    self.__dict__ = self.build(self)

  def build(self, root):
    for key in root:
      if isinstance(root[key], dict):
        root[key] = Config(root[key])

    return root

  def load(self, path):
    with open(path) as f:
      content = f.read()
      self.update(yaml.load(content))

default_config = Config("/etc/gitfs/conf.yaml")
