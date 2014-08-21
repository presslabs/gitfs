from gitfs.utils import split_path_into_components


class TestPathUtils(object):

    def test_split_path_into_components(self):
        empty_path = ''
        empty_path2 = '/'
        path = '/a/b'

        assert split_path_into_components(empty_path) == []
        assert split_path_into_components(empty_path2) == []
        assert split_path_into_components(path) == ['a', 'b']
