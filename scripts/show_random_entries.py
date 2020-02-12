from random import shuffle
from bbox import AnnotationContainer
import argparse
import cv2

ALIAS_NAME = 'contshow'

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Show entries from annotation container.')

	parser.add_argument('container', metavar='FILE', type=str, help='Container')
	parser.add_argument('-l', '--labels', type=str, nargs='*', help='Only show these labels')
	parser.add_argument('-p', '--prune', action='store_true', help='Prune empty entries')
	parser.add_argument('-n', '--name', type=str, nargs='*', help='Names of images to show')
	parser.add_argument('-s', '--shuffle', action='store_true', help='Shuffle images')
	parser.add_argument('-t', '--threshold', type=float, help='Filter detections with confidence')
	args = parser.parse_args()

	container = args.container
	cont = AnnotationContainer.from_file(container)
	if args.labels and len(args.labels) > 0:
		cont = cont.with_selected_labels(args.labels, prune_empty_entries=args.prune, in_place=True)
	if args.threshold is not None:
		assert 0 <= args.threshold <= 1, 'Confidence threshold must be in [0, 1]'
		cont = cont.filter_all_instances_by_threshold(args.threshold, in_place=True)

	if args.name:
		for n in args.name:
			if n not in cont:
				print(n, 'not in container')
			print('Num instances:', len(cont[n].instances))
			cont[n].show()
	else:
		entry_keys = list(cont.entries.keys())
		if args.shuffle:
			shuffle(entry_keys)

		key = None
		i = 0

		while True:
			image = cont.entries[entry_keys[i]].overlaid_on_image()
			image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
			name = cont.entries[entry_keys[i]].image_name

			cv2.namedWindow(name, cv2.WND_PROP_FULLSCREEN)
			cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
			cv2.imshow(name, image)

			key = cv2.waitKey()
			cv2.destroyAllWindows()

			if key == ord('a'):
				i -= 1
			elif key == ord('d'):
				i += 1
			elif key == ord('q'):
				break

			i = i % len(entry_keys)
		cv2.destroyAllWindows()