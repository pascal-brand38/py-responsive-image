'''
MIT License
Copyright (c) 2023 Pascal Brand

exif and file utility functions:
- printExifTags
- getExif(image, fullFilename, ext:str):
- updateFilestat
'''

import json
from datetime import datetime
import shutil
import os
from PIL import ExifTags   # python -m pip install --upgrade pillow

def printExifTags(exif):
  '''
  print exif tags
  '''
  info = None
  for key, val in exif.items():
    if key in ExifTags.TAGS:
      print(f'{key}:{ExifTags.TAGS[key]}:{val}')
      if ExifTags.TAGS[key] == "ExifOffset":   # from https://github.com/python-pillow/Pillow/issues/5863
        info = exif.get_ifd(key)
  if info:
    for key, val in info.items():
      if key in ExifTags.TAGS:
        print(f'{key}:{ExifTags.TAGS[key]}:{val}')


def getExif(image, fullFilename, ext:str):
  '''
  get exif data AND epoch time of creation of the file
  it may take advantage of .json file, as used by google photo, when the
  exif is not found
  '''
  try:
    exif = image.getexif()
  except:
    print('  no exif in ' + fullFilename)
    exif = None

  # printExifTags(exif)
  # 34665===ExifOffset  and  36867===DateTimeOriginal
  dateTimeOriginal = None
  info = None
  if (exif):
    try:
      info = exif.get_ifd(34665)
      if (info):
        dateTimeOriginal = info.get(36867)
    except:
      pass

  if not dateTimeOriginal and ext=='png':
    try:
      dateTimeOriginal = image.info.get('Creation Time')
    except:
      pass

  if not dateTimeOriginal:
    # no acquisition date in exif nor png metadata
    # check if a json file exist (from a google photo for example)
    try:
      with open(fullFilename + '.json', encoding='utf-8') as json_file:
        jsonData = json.load(json_file)
        epoch = int(jsonData['photoTakenTime']['timestamp'])
        dateTimeOriginal = datetime.fromtimestamp(epoch).strftime('%Y:%m:%d %H:%M:%S')
    except:
      pass

  if dateTimeOriginal:
    # set in exif + png metadata
    if info:
      info[36867] = dateTimeOriginal
    epoch = datetime.strptime(dateTimeOriginal, '%Y:%m:%d %H:%M:%S').timestamp()
  else:
    epoch = 0

  return exif, epoch


def updateFilestat(srcFullFilename, dstFullFilename, epoch):
  '''
  update stat file of dstFullFilename given srcFullFilename, as well as the
  epoch time when not zero
  '''
  shutil.copystat(srcFullFilename, dstFullFilename)
  if (epoch != 0):
    os.utime(dstFullFilename, (epoch, epoch))
