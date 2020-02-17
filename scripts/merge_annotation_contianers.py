import argparse

from bbox import AnnotationContainer
import gc


ALIAS_NAME = 'contmerge'

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Merge two or more annotationcontainers')

    parser.add_argument('containers', metavar='FILE', type=str, nargs='*',
                        help='File(s) to merge')
    parser.add_argument('-n', '--nms', type=float,
                        help='If specified, non-maximum suppression is applied with ' +
                        'the given IoU threshold whenever there same entry is mentioned in both containers.')
    parser.add_argument('-o', '--output', type=str, help='Output filename. If not set, user will be ' +
                        'prompted by request for output filename during runtime.')
    args = parser.parse_args()
    if args.output is None:
        output_file_name = input('Write file to: ')
    else:
        output_file_name = args.output

    cnt = None
    for to_merge in args.containers:
        print(f'Merging container {to_merge} ...'.ljust(70), end='')
        try:
            new_cont = AnnotationContainer.from_file(to_merge)
            if cnt is None:
                cnt = new_cont
            else:
                cnt.merge(new_cont, merge_instance_iou=args.nms, destructively=True)
            del new_cont
            gc.collect()
        except Exception as e:
            print('\tFailed!')
            print(e)
            continue
        print('\tOK')

    cnt.to_file(output_file_name)
