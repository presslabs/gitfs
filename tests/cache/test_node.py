from gitfs.cache.node import Node


class TestNode(object):
    def test_node(self):
        node = Node('prev', 'next', 'data')
        assert node.prev == 'prev'
        assert node.next == 'next'
        assert node.data == 'data'
