class Config(dict):
  def __init__(self, *args, **kwargs):
    super(Config, self).__init__(*args, **kwargs)

    self.__dict__ = self.build(self)

  def build(self, root):
    for key in root:
      if isinstance(root[key], dict):
        root[key] = Config(root[key])

    return root
