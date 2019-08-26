import sys
from pathlib import Path

from bbox import AnnotationContainer


ALIAS_NAME = 'contsum'


if __name__ == '__main__':

	if len(sys.argv) == 1:
		print('use with arguments <full path to container> or $PWD <container>')
		quit()

	container = sys.argv[1]
	suffix = container.split('.')[-1]
	if suffix != 'bbox' and suffix != 'json':
		if len(sys.argv) < 2:
			print('if not using 2 arguments, first must be absolute path to container')
			quit()
		container = Path(container) / sys.argv[2]
	AnnotationContainer.from_file(container).summary()
