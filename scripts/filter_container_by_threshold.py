import argparse
from collections import defaultdict
from bbox import AnnotationContainer
from tqdm import tqdm


ALIAS_NAME = 'contthresh'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Filter out instances in a container by confidence threshold. '
                    'Labels[i] is filtered using threshold[i]')

    parser.add_argument('container', help='Container to threshold')
    parser.add_argument('-l', '--labels', type=str, nargs='*', help='List of labels to threshold')
    parser.add_argument('-t', '--threshold', type=float, nargs='*',
                        help='List of thresholds to use for provided labels.')
    parser.add_argument('-r', '--rest', type=float, help='Threshold to use for all other labels. ' +
                        'If no labels provided, this is used for all labels. If no rest is provided, ' +
                        'all other labels is threshold with 0.0')
    parser.add_argument('-c', '--cleanup', action='store_true', help='Remove all empty entries after thresholding')
    args = parser.parse_args()

    if args.labels and args.threshold:
        assert len(args.labels) == len(args.threshold)
    if args.threshold is None:
        args.threshold = []
    if args.labels is None:
        args.labels = []

    for t in args.threshold:
        assert 0 <= t <= 1

    cont = AnnotationContainer.from_file(args.container)
    labels = cont.get_instance_labels()

    threshold = {}
    for l in labels:
        if l in args.labels:
            threshold[l] = args.threshold[args.labels.index(l)]
        else:
             threshold[l] = args.rest if args.rest else 0.0

    current_threshold = defaultdict(lambda: 1.1)
    for e in cont:
        for i in e:
            if current_threshold[i.label] > i.score:
                current_threshold[i.label] = i.score

    print('==== Current lowest score for each label: ====')
    for l in sorted(list(current_threshold.keys())):
        print('\t', l.ljust(15), current_threshold[l])
    print()
    print('==== Filtering instances with threshold: ====')
    for l, t in threshold.items():
        print('\t', l.ljust(15), t)

    if input('\nContinue? [y/n]: ') != 'y':
        quit()

    for e in tqdm(cont):
        e.instances = [i for i in e if i.score >= threshold[i.label]]

    if args.cleanup:
        print('==== Cleanup: Removing empty entries ====')
        cont.without_empty_entries(in_place=True)

    cont.summary()
    cont.to_file(args.container)
