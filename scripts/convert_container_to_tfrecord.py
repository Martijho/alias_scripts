from bbox import AnnotationContainer
from bbox.contrib.detection.tensorflow import TensorflowObjectDetector
from bbox.converters.tfrecord import TFRecordConverter
from bbox.contrib.data_augmentation import get_random_fisheye_transform

from pathlib import Path
from tqdm import tqdm_notebook as tqdm

from matplotlib import pyplot as plt
import matplotlib
matplotlib.rc('figure', figsize=(16, 12))

import argparse


ALIAS_NAME = 'cont2tfrecord'


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Converts annotationcontainer to tfrecord')
    parser.add_argument('container', help='Container to select labels from')
    parser.add_argument('labelmap', type=str, help='labelmap.txt to go alongside record')
    parser.add_argument('output', help='Output .tfrecord file')
    parser.add_argument('-d', '--dry_run', action='store_true', help='Perform a test run to view annotations to be converted')
    parser.add_argument('-a', '--augment', action='store_true', help='Augment images with prob 0.5')

    args = parser.parse_args()

    augmentation = get_random_fisheye_transform(0.5) if args.augment else None

    labelmap = {}
    for k, v in TensorflowObjectDetector.load_labels_from_pbtxt(args.labelmap).items():
        labelmap[v] = k
    labels_to_record_list = list(labelmap.keys())
    print(labels_to_record_list)

    container = AnnotationContainer.from_file(args.container)

    if args.dry_run:
        container = container.with_selected_labels(labels_to_record_list)

        for e in container:
            if augmentation is not None:
                new_e, new_img = augmentation(e)
                new_e.parent = container

                plt.subplot(121)
                plt.title('Augmented')
                plt.axis('off')
                plt.imshow(new_e.overlaid_on_image(new_img))

                plt.subplot(122)

            plt.title('Annotation')
            plt.axis('off')
            plt.imshow(e.overlaid_on_image())
            plt.show()
    else:
        TFRecordConverter().to_file(
            args.output,
            container,
            labels=labels_to_record_list,
            max_image_size=640,
            augmentation_function=augmentation
        )

