import heapq

class TopNPriorityQueue:
    def __init__(self, n):
        """
        The function initializes a class instance with an empty heap, a set for unique elements, and a
        specified value for n.
        
        :param n: The parameter `n` in the `__init__` method represents the size or capacity of the heap
        data structure that is being initialized. This parameter is used to determine the maximum number
        of elements that can be stored in the heap
        """
        self.heap = []
        self.unique_elements = set()
        self.n = n

    def push(self, element):
        """
        This Python function pushes elements onto a heap while ensuring uniqueness based on a specific
        attribute.
        
        :param element: It is a method named `push` that adds elements to a heap while maintaining
        uniqueness based on the `provider_npi` attribute of the elements.
        The method uses a heap (`self.heap`) to store elements and a set
        (`self.unique_elements`) to keep track
        """
        if element.provider_npi not in self.unique_elements:
            heapq.heappush(self.heap, element)
            # non-duplicate keys
            self.unique_elements.add(element.provider_npi)
            if len(self.heap) > self.n:
                removed_element = heapq.heappop(self.heap)
                self.unique_elements.remove(removed_element.provider_npi)

    def get_top_n(self):
        """
        The function `get_top_n` returns the top n elements from a heap in descending order.
        :return: A sorted list of elements in the heap in descending order.
        """
        return sorted(self.heap, reverse=True)

    def is_empty(self):
        """
        The function `is_empty` checks if the heap is empty by comparing the length of the heap to zero.
        :return: The `is_empty` method is returning a boolean value indicating whether the heap is empty
        or not. It returns `True` if the length of the heap is 0, meaning the heap is empty, and `False`
        otherwise.
        """
        return (len(self.heap) == 0)
