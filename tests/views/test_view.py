from gitfs.views.view import View


class SimpleView(View):
    pass


class TestView(object):
    def test_get_attr(self):
        simple_view = SimpleView(**{
            'uid': 1,
            'gid': 1,
            'mount_time': "now",
        })

        asserted_getattr = {
            'st_uid': 1,
            'st_gid': 1,
            'st_ctime': "now",
            'st_mtime': "now",
        }
        assert simple_view.getattr() == asserted_getattr
