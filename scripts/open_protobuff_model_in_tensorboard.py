import tensorflow as tf
import argparse
import os

ALIAS_NAME = 'totb'


def get_args():
    parser = argparse.ArgumentParser(description='Export .pb files to tensorboard')
    parser.add_argument('model', help='frozen_inference_graph.pb')
    parser.add_argument('--out', help='log_dir: where event file is written')
    parser.add_argument('--port', default='6006', help='Tensorboard port. Default 6006')
    return parser.parse_args()


if __name__ == '__main__':

    args = get_args()

    model = args.model
    out = args.out if args.out else 'event'

    with tf.Session() as sess:
        model_filename = str(model)
        with tf.gfile.FastGFile(model_filename, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            g_in = tf.import_graph_def(graph_def)

        train_writer = tf.summary.FileWriter(str(out))

        train_writer.add_graph(sess.graph)

    os.system(f'tensorboard --logdir {out} --port {args.port}')
