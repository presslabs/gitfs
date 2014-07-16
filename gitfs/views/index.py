from .view import View


class IndexView(View):
  def readdir(self, path, fh):
    print "I'm reading dirs"
