import sys
from pathlib import Path
import argparse

from bbox import AnnotationContainer


ALIAS_NAME = 'contlabelselect'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Selects probided labels from container')

    parser.add_argument('container', help='Container to select labels from')
    parser.add_argument('-l', '--labels', type=str, nargs='*',
                        help='label(s) to select from container')
    parser.add_argument('-o', '--out_container', type=str,
                        help='Output path to write trimmed container to. ' +
                        'If not provided, default filename will be ' +
                        '\'output_container_label1_label2_...bbox\'')
    parser.add_argument('-r', '--remove_empty', action='store_true', help='Set to remove entries with no instances in trimmed container')
    parser.add_argument('-c', '--clean', action='store_true', help='Remove all entries with invalid path to an image')

    parser.add_argument('-f', '--file', type=str, help='Names or labelmap file. ' +
                        'Read as darknets names file if suffix == .txt, ' +
                        'read as labelmap if suffix == .pbtxt. This option ' +
                        'overwrites labels provided as positional arguments')
    args = parser.parse_args()

    if args.file is not None:
        filename = Path(args.file)
        if filename.suffix == '.txt':
            labels = [l.strip() for l in filename.open('r').readlines() if l.strip() != '']
        elif filename.suffix == '.pbtxt':
            raise NotImplementedError('Parsing labelmap.pbtx files is not implemented yet')
        else:
            raise ValueError(f'{args.file} not recognized as valid label file')
    else:
        assert args.labels is not None, 'Some labels must be provided if no labelmap is given with -f'
        labels = args.labels

    if args.container == args.out_container:
        if input('Are you sure you want to overwrite container? (y/n): ') != 'y':
            quit()

    print('Selected labels:')
    print(labels)
    print('Remove empty entries from trimmed container:', args.remove_empty)
    print('Clean container of entries with non-valid paths to images:', args.clean)

    if args.out_container is None:
            out = 'trimmed_container_{}.bbox'.format('_'.join(args.labels))
    else:
            out = args.out_container


    container = AnnotationContainer.from_file(args.container)
    container.with_selected_labels(labels, in_place=True)
    if args.remove_empty:
        for e in list(container.entries.keys()):
            if len(container.entries[e]) == 0:
                del container.entries[e]
    if args.clean:
        for e in list(container.entries.keys()):
            if container.entries[e].get_image_full_path() is None or not Path(container.entries[e].get_image_full_path()).exists():
                del container.entries[e]

    container.summary()
    container.to_file(out)
