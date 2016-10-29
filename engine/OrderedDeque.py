#   Copyright Alexander Baranin 2016

# wekaref-enabled ordered set, convenient for UI windows stack organization

import weakref

class OrderedDeque():
    """
        Ordered deque with fast order comparison operation (simply by index).
        Most operations are defined on it's element, not on object itself.
    """
    class DequeElement():
        def __init__(self, owner, obj, index, prev = None, next = None):
            self.obj = obj
            self.owner = owner
            self.index = index
            self.prev = prev
            self.next = next

        def moveToHead(self):
            self.owner.moveToHead(self)

    def __init__(self):
        self.root = None
        self.head = None
        self.head_index = -1

    def push(self, obj):
        """Create new element and push it to the tail of deque"""
        self.head_index += 1
        elem = OrderedDeque.DequeElement(self, obj, self.head_index, self.head)
        if self.head is not None:
            self.head.next = elem
        self.head = elem
        if self.root is None:
            self.root = elem
        return elem

    def pushElem(self, elem):
        """Push element to the tail of deque"""
        self.head_index += 1
        elem.index = self.head_index
        elem.prev = self.head
        elem.next = None
        if self.head is not None:
            self.head.next = elem
        self.head = elem
        if self.root is None:
            self.root = elem

    def removeElem(self, elem):
        """Remove element from deque"""
        if self.head is elem:
            self.head = elem.prev
        if self.root is elem:
            self.root = elem.next
        if elem.prev is not None:
            elem.prev.next = elem.next
        if elem.next is not None:
            elem.next.prev = elem.prev

    def removeFirst(self, obj):
        """
            Remove first element, that holds passed object. 
            Returns element deleted, does not throw.
        """
        elem = self.root
        while elem is not None:
            if elem.obj is obj:
                self.removeElem(elem)
                return elem
            elem = elem.next
        return None

    def moveToHead(self, elem):
        self.removeElem(elem)
        self.pushElem(elem)



class WeakOrderedDeque(OrderedDeque):
    def __init__(self):
        super().__init__()

    def push(self, obj):
        weak = weakref.ref(obj, self.onWeakCollect)
        return super().push(weak)

    def onWeakCollect(self, weak):
        self.removeFirst(weak)