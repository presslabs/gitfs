from fuse import Operations, LoggingMixIn


class Router(Operations, LoggingMixIn):
  def __init__(self):
    self.regex = []

  def register(self, regex, cls):
    self.regex.append(regex, cls)

  def get_view(self):
    print 'ok'
