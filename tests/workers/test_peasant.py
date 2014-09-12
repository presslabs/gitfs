from mock import patch

from gitfs.worker.peasant import Peasant


class TestPeasant(object):
    def test_peasent_init(self):
        with patch('gitfs.worker.peasant.Thread'):
            peasant = Peasant(simple_attribute="value")

            assert peasant.simple_attribute == "value"
