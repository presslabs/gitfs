class Node(object):
    def __init__(self, val, key, next=None, prev=None):
        self.val = val
        self.key = key
        self.next = next
        self.prev = prev


class Queue(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.tail = None
        self.head = None
        self.size = 0

    def add(self, val, key):
        node = Node(val, key)

        if self.tail is not None:
            node.next = None
            node.prev = self.tail
            if self.tail.prev:
                self.tail.prev.next = node
        else:
            self.head = node

        self.tail = node

        self.size += 1
        return node

    def remove_from_head(self):
        to_remove = self.head

        if self.head is not self.tail:
            self.head = self.head.next or self.tail
            self.head.prev = None
        else:
            self.head = self.tail = None

        self.size -= 1

        return to_remove

    def move_to_tail(self, node):
        if node.key == self.head.key:
            self.remove_from_head()
        else:
            self.remove(node)
        self.add(node.val, node.key)

    def remove(self, node):
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev

        del node

        self.size -= 1

    def replace(self, node, value):
        node.val = value
        self.move_to_tail(node)

    def show_queue(self):
        node = self.tail
        print "showing queue"
        nodes = []
        while node is not None:
            nodes.append(node.key)
            node = node.prev
        print ",".join(nodes)


class LRUCache(object):

    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = Queue(capacity)
        self.maping = {}

    def get(self, key):
        if key in self.maping and self.maping[key] is not None:
            self.queue.move_to_tail(self.maping[key])
            print "hit", self, self.queue.size, key
            return self.maping[key].val
        print "miss"
        return None

    def set(self, key, value):
        if key in self.maping and self.maping[key]:
            self.queue.replace(self.maping[key], value)
        else:
            if self.queue.size >= self.queue.capacity:
                node = self.queue.remove_from_head()
                # TODO: remove this bug
                self.maping[node.key] = None
                del self.maping[node.key]
                print "delete", node.key, self.queue.show_queue(), self.queue.size
            print "set: ", key, self.queue.size
            node = self.queue.add(value, key)
            self.maping[key] = node
