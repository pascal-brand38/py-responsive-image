'''
MIT License
Copyright (c) 2023 Pascal Brand

TODO
'''

class argsResponsiveImage(object):
  def __init__(self, argsparsed, nb:int|None=None):
    self.args = argsparsed
    self.nb = nb

  def inc(self):
    if self.nb is not None:
      self.nb = self.nb + 1

  def print(self, filename: str, processed: bool):
    if self.nb is not None:
      if (processed):
        print('  + ' + str(self.nb) + ' ' + filename)
      else:
        print('  - ' + str(self.nb) + ' ' + filename)