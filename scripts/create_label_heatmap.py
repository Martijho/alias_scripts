from pathlib import Path
import argparse
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from bbox import AnnotationContainer


ALIAS_NAME = 'contheatmap'


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Plot heatmap for labels in dataset')

    parser.add_argument('container', help='Container to select labels from')
    parser.add_argument('labels', type=str, nargs='*', help='label(s) to select from container')
    parser.add_argument('-s', '--store', action='store_true', help='Store heatmaps')

    args = parser.parse_args()

    container = AnnotationContainer.from_file(args.container)
    analytic = container.analytic()

    heatmaps = {l: analytic.get_label_heatmap(l) for l in tqdm(args.labels)}

    for label, hm in heatmaps.items():
        plt.title('Label: '+label)
        plt.imshow(hm)
        plt.show()
        if args.store:
            np.save(f'{Path(args.container).stem}_{label}_heatmap', hm)
