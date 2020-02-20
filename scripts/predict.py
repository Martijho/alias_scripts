from bbox import AnnotationContainer, AnnotationInstance, AnnotationEntry, BBox, DatasetSourceProvider, ImageSize
from bbox.contrib.detection.darknet import DarknetObjectDetector
from bbox.contrib.detection.tensorflow import TensorflowObjectDetector

from pathlib import Path
import argparse
import numpy as np
from tqdm import tqdm
import cv2

from collections import defaultdict


ALIAS_NAME = 'predict'


def _get_detector_func(model_root):
    files = list(Path(model_root).glob('*'))
    suffix = [f.suffix for f in files]

    # Darknet
    if '.cfg' in suffix and '.weights' in suffix and '.data' in suffix:
        return dn_detector
    if '.pbtxt' in suffix and '.pb' in suffix:
        return tf_detector
    if '.prototxt' in suffix and '.caffemodel' in suffix:
        return caffe_detector

    raise ValueError('No model type recognized')


def caffe_detector(model_root, threshold=.01, box_blending=False, anchors=None):
    from bbox.contrib.detection.caffe import CaffeYoloObjectDetector
    model_root = Path(model_root)
    model_name = model_root.name
    prototxt = model_root / f'{model_name}.prototxt'
    caffemodel = model_root / f'{model_name}.caffemodel'

    if anchors is None:
        anchors = np.array([0.72, 1.67, 1.86, 4.27, 2.83, 8.66, 5.53, 10.47, 10.83, 12.45]).reshape((5, 2))
    if type(anchors) == list:
        anchors = np.array(anchors).reshape(len(anchors)//2, 2)

    names = [l for l in (model_root / 'names.txt').open('r').read().split('\n') if l != '']
    cd = CaffeYoloObjectDetector(
        prototxt,
        caffemodel,
        anchors=anchors,
        labelmap=names,
        detection_score_threshold=threshold,
        nms_iou_threshold=.0 if box_blending else 0.45,
        detector_output_format='relative'
    )
    return cd


def dn_detector(model_root, threshold=.01, box_blending=False):
    darknet_path = Path('/home/martin/repos/darknet_mirror')
    model_root = Path(model_root)
    model_name = model_root.name
    data = model_root / f'{model_name}.data'
    cfg = model_root / f'{model_name}.cfg'
    weights = model_root / f'{model_name}.weights'

    dnd = DarknetObjectDetector(
        darknet_path,
        cfg,
        weights,
        data,
        detection_score_threshold=threshold,
        nms_iou_threshold=.0 if box_blending else .45
    )
    return dnd


def tf_detector(model_root, threshold=.01, box_blending=False):
    assert not box_blending, 'TensorflowObjectDetector does not support blending'
    model_root = Path(model_root)
    labelmap = model_root / 'label_map.pbtxt'
    model = model_root / 'frozen_inference_graph.pb'
    tfd = TensorflowObjectDetector(
        model,
        labelmap,
        detection_score_threshold=threshold
    )
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


def load_preview_image(path):
    buffer = open(path, 'rb').read()
    img = np.frombuffer(buffer, dtype=np.float16).astype(np.float32)
    img = img.reshape((3, 480, 640)).transpose((1, 2, 0))
    return (img*255).astype(np.uint8)


def detect_on_preview_dir(preview_data, detector):
    dsp = DatasetSourceProvider()
    dsp.add_source(preview_data, 'predicted')
    container = AnnotationContainer(dataset_source_provider=dsp)

    for image_path in Path(preview_data).glob('preview*'):
        image = load_preview_image(str(image_path))
        det = detector.detect_image(image)

        e = AnnotationEntry(image_path.name, ImageSize.from_image(image), 'predicted', instances=det)
        container.add_entry(e)

    return container


def predict_on_video(video_file, detector):
    def frame_generator():
        vidcap = cv2.VideoCapture(str(video_file))

        frame = 0
        while True:
            success, image = vidcap.read()
            if success:  # and frame < 500:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                yield frame, image
                frame += 1
            else:
                break
    name = Path(video_file).stem
    colors = defaultdict(lambda: np.random.randint(0, 255, 3))
    cv2.namedWindow(name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    for frame_nr, image in frame_generator():
        for i in detector.detect_image(image):
            image = i.bbox.overlaid_on_image(image, colors[i.label])
        cv2.imshow(name, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        if cv2.waitKey(10) == ord('q'):
            break


def main(args):
    thresh = .01 if args.box_blending else args.threshold
    get_detector = _get_detector_func(args.model)
    if get_detector == caffe_detector:
        detector = get_detector(args.model, thresh, box_blending=args.box_blending, anchors=args.anchors)
    else:
        detector = _get_detector_func(args.model)(args.model, thresh, box_blending=args.box_blending)

    with detector:
        if args.container:
            gt = AnnotationContainer.from_file(args.container)
            pred = detector.detect_on_annotation_container(gt)  # .with_selected_labels(['person'])

            if args.box_blending and type(detector) == DarknetObjectDetector:
                pred = _blend_boxes(pred)
                pred.filter_all_instances_by_threshold(args.threshold, in_place=True)
            pred.as_evaluated_against(gt).summary()

        elif args.images:
            pred = detector.detect_on_image_folder(args.images, dataset_name='predicted')
            if args.box_blending and type(detector) == DarknetObjectDetector:
                pred = _blend_boxes(pred)
                pred.filter_all_instances_by_threshold(args.threshold, in_place=True)

        elif args.preview:
            pred = detect_on_preview_dir(args.preview, detector)
            if args.box_blending and type(detector) == DarknetObjectDetector:
                pred = _blend_boxes(pred)
                pred.filter_all_instances_by_threshold(args.threshold, in_place=True)

        elif args.video:
            predict_on_video(args.video, detector)

    if args.output:
        pred.to_file(args.output)


def get_args():
    parser = argparse.ArgumentParser(description='Predict on data with a model')
    parser.add_argument('model', type=str, help='Model')
    parser.add_argument('-o', '--output', type=str, help='Output container path')
    parser.add_argument('-c', '--container', type=str, help='Predict on AnnotationContainer')
    parser.add_argument('-i', '--images', type=str, help='Predict on images in directory')
    parser.add_argument('-t', '--threshold', default=0.01, type=float, help='Confidence threshold')
    parser.add_argument('-p', '--preview', type=str, help='Predict on directory of raw preview images')
    parser.add_argument('-v', '--video', type=str, help='Predict on video file. Overlay results live')
    parser.add_argument(
        '-b', '--box_blending',
        action='store_true',
        help='Instead of NMS to select from overlapping boxes, use a weighted mean of overlaps'
    )
    parser.add_argument(
        '-a', '--anchors',
        type=float,
        nargs='*',
        default=[0.72, 1.67, 1.86, 4.27, 2.83, 8.66, 5.53, 10.47, 10.83, 12.45],
        help='Anchors to use with yolo detection (caffe). '
             'Defaults to [0.72, 1.67, 1.86, 4.27, 2.83, 8.66, 5.53, 10.47, 10.83, 12.45]'
    )
    args = parser.parse_args()

    arg_data = [1 for d in [args.container, args.images, args.preview, args.video] if d is not None]
    if sum(arg_data) != 1:
        raise ValueError('One (and only one) data set to infer on has to be defined')

    if args.output:
        assert Path(args.output).parent.exists(), 'Path to output directory does not exists'
        if Path(args.output).exists():
            if input('Output path exists. Overwrite? [y/n]: ') != 'y':
                quit()

    return args


if __name__ == '__main__':
    main(get_args())
