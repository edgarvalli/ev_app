def is_bidimensional(tup):
    return isinstance(tup, tuple) and all(isinstance(i, (tuple, list)) for i in tup)
