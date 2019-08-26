from pathlib import Path
from bbox import AnnotationContainer
import argparse

ALIAS_NAME = 'contpath'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Change root path to datasets in container.')

    parser.add_argument('container', metavar='FILE', type=str, help='Container')
    parser.add_argument('-a', '--all', type=str, help='Give all datasets this path as root')
    parser.add_argument('-i', '--interactive', action='store_true', help='Sets script in interactive mode where you provide paths for all subsets')
    args = parser.parse_args()

    cont = AnnotationContainer.from_file(args.container)
    dsp = cont.dataset_source_provider.dataset_sources

    if args.interactive:
        print('\tInteractive mode: provide path for each of the following subsets')
        for dataset, subset in list(dsp.keys()):
            root_path = Path(input(f'[({dataset}, {subset})] ->  '))
            if root_path.exists():
                print('\033[32mOK\033[0m')
                dsp[(dataset, subset)] = root_path
            else:
                print('\033[31mWarning: can not find this directory.\033[0m', end=' ')
                if input('Add anyway?  [y/n] ') == 'y':
                    dsp[(dataset, subset)] = root_path
    elif args.all:
        root_path = Path(args.all)
        if not root_path.exists():
            print('\033[31mWarning: can not find this directory.\033[0m', end=' ')
            if input('Add anyway?  [y/n] ') != 'y':
                quit()
        for k in list(dsp.keys()):
            dsp[k] = root_path
    else:
        raise ValueError('Script must either be run in interactive mode, or --all must be set')

    cont.summary()
    cont.to_file(args.container)
