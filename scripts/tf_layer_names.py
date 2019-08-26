from tensorflow.python.tools import inspect_checkpoint as chkp
import tensorflow as tf
import argparse


ALIAS_NAME = 'tflayername'


def should_be_suppressed(name, suppress_list):
    if suppress_list is None:
        return False
    for sup in suppress_list:
        if sup in name:
            return True
    return False


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Outputs the layer names of a tensorflow graph')
    parser.add_argument('graph', help='Path to tensorflow .pb file or model checkpoint')
    parser.add_argument('--suppress', '-s', type=str, nargs='*',
                        help='Layer names that contain one of these substring(s) will not be output')
    parser.add_argument('--output', '-o', type=str, help='Name of output file')
    args = parser.parse_args()

    if not args.graph.endswith('.pb'):
        chkp.print_tensors_in_checkpoint_file(args.graph, tensor_name='', all_tensors=False, all_tensor_names=True)
        quit()

    names = []
    det_graph = tf.Graph()
    with det_graph.as_default():
        graph_def = tf.GraphDef()
        with tf.gfile.GFile(args.graph, 'rb') as fid:
            graph_def.ParseFromString(fid.read())
            tf.import_graph_def(graph_def, name='')

            for m in tf.Session().graph.get_operations():
                if should_be_suppressed(m.name, args.suppress):
                    continue
                names.append(m.name)

    if args.output is None:
        for n in names:
            print(n)
    else:
        with open(args.output, 'w') as writer:
            for n in names:
                writer.write(n + '\n')
