# Alias scripts
This repo is intended as a quality of life improvement for those that use BBox-annotationcontainers regularly.

### Setup

To setup, run
```bash
python setup.py
```
from the repo root-directory.
This script will create a `.bashrc_autogen_alias` file which will be sourced from `~/.bashrc_alias`.
Source either that file or `.bashrc_autoget_alias` from your `.bashrc`

### Scripts and their alias
#### `contpath`
Replaces the image directory path stored in a container. Run with `-a` to set a path for all (dataset, subset) 
or `-i` to run interactively. You will be prompted with each (dataset, subset) and must provide a path for each. 
Tip: `-a` allows you to use autocomplete
#### `contsum`
Outputs the container summary for a container.
#### `contthresh`
Filters annotations in a container by confidence threshold.
#### `contmerge`
Merges two or more containers. Run with `-n` to apply non-maximum suppression on each entry after merging
#### `predict`
Predicts with a model. Input can be a container (`-c <path>`), directory of images (`-i <path>`) 
or a directory of preview-images from autozoom feedback (`-p <path>`). The option `-b` runs box-blending instead of NMS 
on the inferences, but dont use it.
#### `cont2tfrecord`
Takes a container and labelmap and outputs the annotations as a tf-record. Make sure that all images the container 
reference is found by running `contsum`. 
#### `cont2video`
Applies a container to all its images and writes it as a video. 
All images must have a integer name (i.e: `1.jpg` or `0001.jpg`)
#### `contlabelselect`
Takes a container and some labels and outputs a new container with only annotations with the provided labels. 
Labels can be provided as a manually entered list with `-l` (i.e: `-l person head face`) or as a path to a labelmap or 
names file with `-f`. The option `-r` will remove all entries without annotations after filtering by labels, and 
`-c` will remove all entries where the image was not found
#### `contload`
Takes a container path and opens a interactive ipython shell where the container is loaded as `container`. The script 
also imports the packages cv2, numpy and Path along side AnnotationContainer
#### `totb`
Takes a frozen_inference_graph.pb file (or indeed any other protobuff model) and opens it in tensorboard for inspection.
All tensorboard options can be used, like `--port <nr>` to change the tensorboard port.
#### `contheatmap`
Takes a container and labels and creates a heatmap for each label to show what areas of an image is most likely to 
contain each label. Use the option `-s` to store the heatmaps as numpy files next to the container with the 
`_heatmap.npy` suffix.
#### `contshow`
Used to inspect annotations in a container. Navigate through images with `a` and `d` and use `q` to quit. 
Some options are provided so the script can be used for different usecases. 
* `-l <one or more labels>` will limit which annotations will be shown
* `-p` will remove not show entries without annotations
* `-b <one or more image names>` will show only selected images and their annotations
* `-s` will shuffle the entries before showing them 
* `-t <threshold>` will filter annotations by a confidence threshold before showing
* `-m <max number of images>` will show only `-m` images before quiting. 

### Create a new alias in this repo
To create a new alias-script, simply write your script (making sure it only operates on absolute paths) and add it to
the `scripts` directory and run `setup.py`. For your script to be indexed by setup.py, add a variable `ALIAS_NAME` 
somewhere in the first lines of code, that contains the alias name you want. I.E: `ALIAS_NAME = contsum`  

### TODO:
    * Testing for all scripts

