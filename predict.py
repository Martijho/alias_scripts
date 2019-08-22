from bbox import AnnotationContainer, AnnotationInstance, AnnotationEntry, BBox
from bbox.contrib.detection.darknet import DarknetObjectDetector
from bbox.contrib.detection.tensorflow import TensorflowObjectDetector

from pathlib import Path
import argparse
import numpy as np
from tqdm import tqdm


def _get_detector_func(model_root):
    files = list(Path(model_root).glob('*'))
    suffix = [f.suffix for f in files]

    # Darknet
    if '.cfg' in suffix and '.weights' in suffix and '.data' in suffix:
        return dn_detector
    if '.pbtxt' in suffix and '.pb' in suffix:
        return tf_detector

    raise ValueError('No model type recognized')


def dn_detector(model_root, threshold=.01, box_blending=False):
    darknet_path = Path('/home/martin/repos/darknet_mirror')
    model_root = Path(model_root)
    model_name = model_root.name
    data = model_root / f'{model_name}.data'
    cfg = model_root / f'{model_name}.cfg'
    weights = model_root / f'{model_name}.weights'

    dnd = DarknetObjectDetector(darknet_path, cfg, weights, data,
                                detection_score_threshold=threshold,
                                nms_iou_threshold=.0 if box_blending else .45)
    return dnd


def tf_detector(model_root, threshold=.01, box_blending=False):
    assert not box_blending, 'TensorflowObjectDetector does not support blending'
    model_root = Path(model_root)
    labelmap = model_root / 'label_map.pbtxt'
    model = model_root / 'frozen_inference_graph.pb'
    tfd = TensorflowObjectDetector(model, labelmap,
                                   detection_score_threshold=threshold)
    return tfd


def _blend_boxes(pred):
    def blend_boxes(group, label, coordinate_mode):
        scores = np.array([i.score for i in group])
        xmins = np.array([i.xmin for i in group])
        ymins = np.array([i.ymin for i in group])
        xmaxs = np.array([i.xmax for i in group])
        ymaxs = np.array([i.ymax for i in group])

        xmin = np.sum(xmins * scores) / np.sum(scores)
        ymin = np.sum(ymins * scores) / np.sum(scores)
        xmax = np.sum(xmaxs * scores) / np.sum(scores)
        ymax = np.sum(ymaxs * scores) / np.sum(scores)
        score = scores.max()  # np.sum(scores * scores) / np.sum(scores)

        return AnnotationInstance(bbox=BBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax,
                                            label=label, score=score,
                                            coordinate_mode=coordinate_mode))

    for pred_entry in tqdm(pred, desc='blending'):
        predictions = [i for i in pred_entry]

        iou_map = pred_entry.compute_iou(pred_entry)
        iou_map = {(a, b): val for (a, b), val in iou_map.items()
                   if a != b and val >= .45 and a.label == b.label}
        predictions = list(sorted(predictions, key=lambda x: -x.score))
        iou_groups = {a: [b for (a_, b), _ in iou_map.items() if a == a_] for a in predictions}
        used = set()

        output = []
        for a, others in iou_groups.items():
            if len(others) >= 1:
                group = set(others)
                group.add(a)
                group = group.difference(used)
                if len(group) == 0:
                    continue
                used = used.union(group)
                output.append(blend_boxes(group, a.label, a.bbox.coordinate_mode))
            else:
                output.append(a)
        pred_entry.instances = []
        for i in output:
            pred_entry.add_instance(i)

    return pred


def main(args):
    thresh = .01 if args.box_blending else args.threshold
    detector = _get_detector_func(args.model)(args.model, thresh, box_blending=args.box_blending)

    with detector:
        if args.container:
            gt = AnnotationContainer.from_file(args.container)
            pred = detector.detect_on_annotation_container(gt)  # .with_selected_labels(['person'])

            if args.box_blending and type(detector) == DarknetObjectDetector:
                pred = _blend_boxes(pred)
                pred.filter_all_instances_by_threshold(args.threshold, in_place=True)
            pred.as_evaluated_against(gt).summary()

        if args.images:
            pred = detector.detect_on_image_folder(args.images, dataset_name='predicted')
            if args.box_blending and type(detector) == DarknetObjectDetector:
                pred = _blend_boxes(pred)
                pred.filter_all_instances_by_threshold(args.threshold, in_place=True)

    if args.output:
        pred.to_file(args.output)


def get_args():
    parser = argparse.ArgumentParser(description='Predict on data with a model')
    parser.add_argument('model', type=str, help='Model')
    parser.add_argument('-o', '--output', type=str, help='Output container path')
    parser.add_argument('-c', '--container', type=str, help='Predict on AnnotationContainer')
    parser.add_argument('-i', '--images', type=str, help='Predict on images in directory')
    parser.add_argument('-t', '--threshold', default=0.01, type=float, help='Confidence threshold')
    parser.add_argument('-b', '--box_blending', action='store_true', help='Instead of NMS to select from overlapping boxes, use a weighted mean of overlaps')
    args = parser.parse_args()

    if args.container is None and args.images is None:
        raise ValueError('No data to infer on')
    if args.container and args.images:
        raise ValueError('Only one data set to infer on is allowed')

    if args.output:
        assert Path(args.output).parent.exists(), 'Path to output directory does not exists'
        if Path(args.output).exists():
            if input('Output path exists. Overwrite? [y/n]: ') != 'y':
                quit()

    return args


if __name__ == '__main__':
    main(get_args())
