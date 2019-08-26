from bbox import AnnotationContainer, AnnotationEntry, AnnotationInstance, BBox, DatasetSourceProvider
import json
import argparse


ALIAS_NAME = 'json2cont'


def build_entry(e, dataset_name=None, dataset_subset=None):
    entry = AnnotationEntry(
        e['image_path'],
        (e['image_size']['width'], e['image_size']['height']),
        dataset_name=dataset_name,
        dataset_subset=dataset_subset
    )

    for i in e['instances']:
        i = i['bbox']
        entry.add_instance(AnnotationInstance(bbox=BBox(
            xmin = i['xmin'], ymin = i['ymin'],
            xmax = i['xmax'], ymax = i['ymax'],
            label = i['label'], score = i['score'],
            source = i['source'], coordinate_mode = i['coordinate_mode']
        )))

    return entry


def main(data, args):

    dsp = DatasetSourceProvider() if args.image_dir else None
    if args.image_dir:
        dsp.add_source(args.image_dir, args.dataset_name, args.dataset_subset)

    container = AnnotationContainer(dataset_source_provider=dsp)

    for e in data['entries']:

        entry = build_entry(e, args.dataset_name, args.dataset_subset)
        container.add_entry(entry)
        entry.dataset_name = args.dataset_name
        if args.dataset_subset:
            args.dataset_subset

    container.summary()

    container.to_file(args.output)

def parse_args():
    parser = argparse.ArgumentParser('Convert labeltool output json to AnnotationContainer')
    parser.add_argument('json', help='Annotation tool output json')
    parser.add_argument('output', help='AnnotationContainer output path')
    parser.add_argument('-i', '--image_dir', type=str, help='Path to image dir')
    parser.add_argument('-n', '--dataset_name', type=str, default='annotated', help='dataset name')
    parser.add_argument('-s', '--dataset_subset', type=str, default=None, help='dataset subset name')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    data = json.load(open(args.json, 'rb'))
    main(data, args)
