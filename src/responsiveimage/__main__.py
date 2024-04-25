'''
MIT License
Copyright (c) 2023 Pascal Brand

Main function of responsiveimage package
'''

import argparse
import os
import sys
from typing import List, Tuple
import filetype
from . import copy_image
from . import pil_image
from . import mp4
from . import argsResponsiveImage

def _createParser() -> argparse.ArgumentParser:
  '''
  parse commandline options
  '''
  parser = argparse.ArgumentParser(
     prog='responsiveimage',
     description='Create different image versions (size, quality, format) from original images',
     formatter_class=argparse.RawTextHelpFormatter
     )

  # parser.add_argument('--rotate',
  #                     help='',
  #                     required=False,
  #                     default=False,
  #                     action='store_true')
  # parser.add_argument('--no-rafale',
  #                     help='',
  #                     required=False,
  #                     default=False,
  #                     action='store_true')
  parser.add_argument('--src-dir',
                      help='source directory. Default: /tmp/toreduce',
                      required=False,
                      default='/tmp/toreduce')
  parser.add_argument('--dst-dir',
                      help='destination directory. Default: /tmp/reduced',
                      required=False,
                      default='/tmp/reduced')
  parser.add_argument('--size',
                      help='list of sizes, separated by commas, of different scale. Ex: 1024,512. Default: 1920px if --height not set',
                      required=False,
                      default=None)
  parser.add_argument('--height',
                      help='list of heights, separated by commas, of different scale. Ex: 1024,512. Cannot be used when --size',
                      required=False,
                      default=None)
  parser.add_argument('--export-to-webp',
                      help='png and jpg are exported in webp format too',
                      required=False,
                      default=False,
                      action='store_true')
  parser.add_argument('--recursive',
                      help='recursive into subdirectories',
                      required=False,
                      default=False,
                      action='store_true')
  parser.add_argument('--mp4-as-gif',
                      help='mp4 saved as .gif and .webo',
                      required=False,
                      default=False,
                      action='store_true')
  parser.add_argument('--add-name',
                      help='list of added name. Default is nothing when a single transform, or size otherwise',
                      required=False,
                      default=None)
  parser.add_argument('--format',
                      help='list of formats, separated by commas. Default: jpg,png,webp,gif,svg,mp4,mts,avi,wmv,mov',
                      required=False,
                      default='jpg,png,webp,gif,svg,mp4,mts,avi,wmv,mov')
  parser.add_argument('--crop',
                      help='x1,y1,x2,y2: crop the original image before rescaling',
                      required=False,
                      default=None)
  parser.add_argument('--force',
                      help='rewrite files',
                      required=False,
                      default=False,
                      action='store_true')

  return parser

def extract(args: argsResponsiveImage.argsResponsiveImage) -> Tuple[set, List[str]]:
  '''
  main function of python package responsiveimage
  '''
  extensionSkipped = set()
  fileFailed = []

  savedSrcDir = args.args.src_dir
  savedDstDir = args.args.dst_dir

  if not os.path.isdir(args.args.dst_dir):
    os.mkdir(args.args.dst_dir)

  pil_image_filename = []
  pil_image_extension = []
  video_filename = []
  video_extension = []
  copy_filename = []
  copy_extension = []

  # TODO: parallel multiprocessing as https://superfastpython.com/multiprocessing-pool-python/#Multiprocessing_Pool_Example
  # https://stackoverflow.com/questions/5442910/how-to-use-multiprocessing-pool-map-with-multiple-arguments
  # https://stackoverflow.com/questions/5442910/how-to-use-multiprocessing-pool-map-with-multiple-arguments/5443941#5443941
  print('Inspecting ' + args.args.src_dir)
  filenames = os.listdir(args.args.src_dir)
  print('Computing extensions of ' + str(len(filenames)) + ' files')
  for filename in filenames:
    if not os.path.isfile(os.path.join(args.args.src_dir, filename)):
      if (args.args.recursive):
        args.args.src_dir = os.path.join(args.args.src_dir, filename)
        args.args.dst_dir = os.path.join(args.args.dst_dir, filename)
        es, ff = extract(args)
        extensionSkipped = extensionSkipped.union(es)
        fileFailed.append(ff)
        args.args.src_dir = savedSrcDir
        args.args.dst_dir = savedDstDir
      continue

    kind = filetype.guess(args.args.src_dir + '/' + filename)
    if kind is None:
      (_, extension) = os.path.splitext(filename)
      if extension != '':
        extension = extension[1:].lower()
    else:
      extension = kind.extension

    # See kind.EXTENSION for supported extensions
    if extension not in args.args.format:
      extensionSkipped.add(extension)
    else:
      if extension in [ 'jpg', 'png', 'webp' ]:
        pil_image_filename.append(filename)
        pil_image_extension.append(extension)
      elif extension in [ 'mp4', 'mts', 'avi', 'wmv', 'mov' ]:
        video_filename.append(filename)
        video_extension.append(extension)
      elif extension in [ 'gif', 'svg' ]:
        copy_filename.append(filename)
        copy_extension.append(extension)
      else:
        print('File extension ' + extension + ' not supported - file ' + filename)
        extensionSkipped.add(extension)

  pil_image_nb = list(range(args.nb, args.nb+len(pil_image_filename)))
  args.add(len(pil_image_filename))
  copy_nb = list(range(args.nb, args.nb+len(copy_filename)))
  args.add(len(copy_filename))
  video_nb = list(range(args.nb, args.nb+len(video_filename)))
  args.add(len(video_filename))

  for i in range(len(pil_image_filename)):
    pil_image.responsive(args, pil_image_filename[i], pil_image_extension[i], pil_image_nb[i])
  for i in range(len(copy_filename)):
    copy_image.responsive(args, copy_filename[i], copy_extension[i], copy_nb[i])
  for i in range(len(video_filename)):
    mp4.responsive(args, video_filename[i], video_nb[i])

  return extensionSkipped, fileFailed


def main(cmdargs: List[str]) -> Tuple[set, List[str]]:
  '''
  main function of python package responsiveimage
  '''
  parser = _createParser()
  args = argsResponsiveImage.argsResponsiveImage(parser.parse_args(cmdargs), 0)
  return extract(args)


if __name__ == "__main__":
  extensionSkipped, fileFailed = main(sys.argv[1:])
  print('Skipped extension: ', extensionSkipped)
  print('Files Failed: ', fileFailed)


# TODO: Skipped extension:  {'xls', 'zip', 'ini'}


'''
      try:
        if extension in [ 'jpg', 'png', 'webp' ]:
          pil_image.responsive(args, filename, extension)
        elif extension in [ 'mp4', 'mts', 'avi', 'wmv', 'mov' ]:
          mp4.responsive(args, filename)
        elif extension in [ 'gif', 'svg' ]:
          copy_image.responsive(args, filename, extension)
        else:
          print('File extension ' + extension + ' not supported - file ' + filename)
          extensionSkipped.add(extension)
      except:
        print('File crash: ' + filename)
        copy_image.responsive(args, filename, extension)
        fileFailed.append(filename)
'''