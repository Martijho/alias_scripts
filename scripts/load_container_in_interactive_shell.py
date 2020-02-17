from bbox import AnnotationContainer
import cv2
import numpy as np
import argparse
from pathlib import Path

ALIAS_NAME = 'contload'
ALIAS_OVERRIDE = 'alias "contload"="ipython -i <PATH>"'

parser = argparse.ArgumentParser(description='Load container interactively')

parser.add_argument('container', metavar='FILE', type=str, help='Container')
args = parser.parse_args()

if not Path(args.container).exists():
    print('Container does not exists')
    quit()

print('Imported:')
print('\t bbox.AnnotationContainer')
print('\t cv2')
print('\t numpy')
print('\t pathlib.Path')
print()
print('Loaded', args.container, 'as \"container\"')
print()

container = AnnotationContainer.from_file(args.container)