from mock import MagicMock, patch
from gitfs.cache import CachedIgnore


class TestCachedIgnore(object):
    def test_init(self):
        mocked_os = MagicMock()
        mocked_os.path.exists.return_value = True
        mocked_re = MagicMock()
        mocked_re.findall.return_value = [[None, None, "found"]]

        with patch("gitfs.cache.gitignore.open", create=True) as mocked_open:
            mocked_file = mocked_open.return_value.__enter__.return_value
            mocked_file.read.return_value = "file"

            with patch.multiple("gitfs.cache.gitignore", os=mocked_os,
                                re=mocked_re):
                gitignore = CachedIgnore("some_file", "some_file")

                assert gitignore.items == ['/.git', '.git/*', '/.git/*',
                                           'file', '/found/*', '/found',
                                           'found']

    def test_update(self):
        gitignore = CachedIgnore()
        gitignore.cache = {"some_key": "some_value"}

        gitignore.update()

        assert gitignore.cache == {}

    def test_contains(self):
        gitignore = CachedIgnore()

        assert '/.git' in gitignore
        assert 'file' not in gitignore
