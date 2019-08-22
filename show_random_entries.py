import sys
from pathlib import Path
from random import shuffle
from bbox import AnnotationContainer
from tqdm import tqdm
import argparse
import matplotlib
matplotlib.rc('figure', figsize=(16, 12))


parser = argparse.ArgumentParser(description='Show random entries from annotation container.')

parser.add_argument('container', metavar='FILE', type=str, help='Container')
parser.add_argument('-l', '--labels', type=str, nargs='*', help='Only show these labels')
parser.add_argument('-p', '--prune', action='store_true', help='Prune empty entries')
parser.add_argument('-n', '--name', type=str, nargs='*', help='Names of images to show')
args = parser.parse_args()

container = args.container
cont = AnnotationContainer.from_file(container)
if args.labels and len(args.labels) > 0:
	cont = cont.with_selected_labels(args.labels, prune_empty_entries=args.prune, in_place=True)

if args.name:
	for n in args.name:
		if n not in cont:
			print(n, 'not in container')
		print('Num instances:', len(cont[n].instances))
		cont[n].show()
else:
	keys = list(cont.entries.keys())
	shuffle(keys)
	for key in tqdm(keys):
		cont.entries[key].show()
