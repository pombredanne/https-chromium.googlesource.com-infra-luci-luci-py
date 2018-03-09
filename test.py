def lines_generator(filename):
    f = open(filename)
    for line in f:
        yield line

class IterableGenerator(object):
  """An iterable generator."""

  def __init__(self, generator_func, **kwargs):
    self.generator_func = generator_func
    self.kwargs = kwargs

  def __iter__(self):
    return self.generator_func(**self.kwargs)

  def next(self):
    return next(self.generator_func(**self.kwargs))



class IterableGenerator2(object):
  """An iterable generator."""

  def __init__(self, generator_func, *args):
    self.generator_func = generator_func
    self.args = args

  def __iter__(self):
    return self.generator_func(*self.args)

  def next(self):
    return next(self.generator_func(*self.args))

req = ['s']

class StreamIter(object):

  def __iter__(self):
    return iter([req])

