'''
MIT License
Copyright (c) 2023 Pascal Brand

Extends argparse
'''

def _check_arg_errors(argsparsed):
  # update argsparsed, and check for errors
  if (argsparsed.size is not None) and (argsparsed.height is not None):
    raise RuntimeError("--size and --height cannot be both set")

  if (argsparsed.size is None) and (argsparsed.height is None):
    argsparsed.size = '1920'

  if (argsparsed.size is not None):
    transform = argsparsed.size.split(',')
  elif (argsparsed.height is not None):
    transform = argsparsed.height.split(',')
  else:
    raise RuntimeError("Developer issue")

  if argsparsed.add_name is None:
    if len(transform) == 1:
      argsparsed.add_name = ''
    else:
      argsparsed.add_name = '-' + ',-'.join(transform)
  else:
    # check length of add_name is same as length of transform
    if argsparsed.add_name.count(',') != len(transform)-1:
      raise RuntimeError("--size (or --height) and --add-name must have the same number of elements")

  return argsparsed

class argsResponsiveImage():
  '''
  extends argparse
  '''
  def __init__(self, argsparsed, nb):
    argsparsed = _check_arg_errors(argsparsed)

    self.args = argsparsed
    self.nb = nb
    self.parameters = {   # TODO: add a commandline option to update it dynamically
      'jpg': {
        'quality': 80,
        'progressive': True,
        'subsampling': '4:2:0',
        },
      'webp': {
        'quality': 80,
      }
    }

  def inc(self):
    '''
    increment the number of processed images
    '''
    if self.nb is not None:
      self.nb = self.nb + 1

  def print(self, filename: str, processed: bool):
    '''
    verbose the number of processed images
    '''
    if self.nb is not None:
      if (processed):
        print('  + ' + str(self.nb) + ' ' + filename)
      else:
        print('  - ' + str(self.nb) + ' ' + filename)
