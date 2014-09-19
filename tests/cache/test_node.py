from gitfs.cache.node import Node


class TestNode(object):
    def test_node(self):
        node = Node()

        node.prev = "prev"
        node.next = "next"
        node.data = "data"

        assert node.prev == 'prev'
        assert node.next == 'next'
        assert node.data == 'data'
