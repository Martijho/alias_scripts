import cv2
from bbox import AnnotationContainer

import argparse
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict
import numpy as np

ALIAS_NAME = 'cont2video'


def get_args():
    parser = argparse.ArgumentParser(description='Create a video of all frames in container with their detections')
    parser.add_argument('container', type=str, nargs='*', help='Containers')
    parser.add_argument('-l', '--labels', type=str, nargs='*', help='Labels to use')
    parser.add_argument('-f', '--fps', default=24, type=int, help='video FPS')
    parser.add_argument('-w', '--watermark', action='store_true', help='Add container name as watermark')
    args = parser.parse_args()

    for c in args.container:
        assert Path(c).exists(), f'{c} does not exists'

    return args


if __name__ == '__main__':
    args = get_args()
    labels = args.labels
    fps = args.fps

    colors = defaultdict(lambda: np.random.randint(0, 255, 3))
    output_files = []
    for container_path in tqdm(args.container, desc='containers'):
        name = Path(container_path).stem
        container = AnnotationContainer.from_file(container_path)
        container.label_to_colour = colors
        video_writer = None

        output_file_name = Path(container_path).parent / f'{Path(container_path).stem}.avi'
        output_files.append(output_file_name)

        if len(labels) > 0:
            container.with_selected_labels(labels, prune_empty_entries=False, in_place=True)
        keys = list(sorted(container.entries.keys(), key=lambda x: int(Path(x).stem)))

        for k in tqdm(keys, desc='frames'):
            e = container[k]
            img = e.overlaid_on_image()

            if video_writer is None:
                h, w = img.shape[:2]
                #                                                         1
                video_writer = cv2.VideoWriter(str(output_file_name), 0, fps, (w, h))

            if args.watermark:
                cv2.putText(img, name,
                            (50, 50), cv2.FONT_HERSHEY_DUPLEX,
                            2, (255, 255, 255), 2)

            video_writer.write(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

        cv2.destroyAllWindows()
        video_writer.release()

    print('To stack videos on top of each other, use: ')
    cmd = 'ffmpeg '
    if len(output_files) > 1:
        for o in output_files:
            cmd += '-i ' + str(o) + ' '
    else:
        cmd += '-i a.avi -i b.avi <...> '
    cmd += '-filter_complex vstack <output name>'
    print(cmd)