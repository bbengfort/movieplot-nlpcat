__author__ = 'benjamin'

class Histogram(dict):
    """
    A dictionary-like object that only allows integers to be stored as
    values on the dictionary to maintain frequency counting. Helper
    methods have also been added to do frequency-like things.
    """

    def __setitem__(self, key, value):
        """
        Only allows integers to be set on the dictionary, raises a
        C{ValueError} if something else attempts to be set on it.
        """
        if not isinstance(value, int):
            raise ValueError("Set only frequency data as integers")
        super(Histogram, self).__setitem__(key, value)

    def increase(self, key, amount):
        if key in self:
            self[key] += amount
        else:
            self[key] = amount

    def decrease(self, key, amount):
        if key in self:
            self[key] -= amount
        else:
            self[key] = 0

    def increment(self, key):
        self.increase(key, 1)
    incr = increment

    def decrement(self, key):
        self.decrease(key, 1)
    decr = decrement

    @property
    def maximum(self):
        key = max(self, key=self.get)
        return key, self[key]
    max = maximum

    @property
    def minimum(self):
        key = min(self, key=self.get)
        return key, self[key]
    min = minimum

    @property
    def average(self):
        return sum(self.values()) / len(self)
    mean = average

    @property
    def total(self):
        return sum(self.values())