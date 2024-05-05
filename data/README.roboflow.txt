
3D printing error - v7 2023-11-26 8:13pm
==============================

This dataset was exported via roboflow.com on November 26, 2023 at 5:16 PM GMT

Roboflow is an end-to-end computer vision platform that helps you
* collaborate with your team on computer vision projects
* collect & organize images
* understand and search unstructured image data
* annotate, and create datasets
* export, train, and deploy computer vision models
* use active learning to improve your dataset over time

For state of the art Computer Vision training notebooks you can use with this dataset,
visit https://github.com/roboflow/notebooks

To find over 100k other datasets and pre-trained models, visit https://universe.roboflow.com

The dataset includes 10757 images.
-spagetti- are annotated in Pascal VOC format.

The following pre-processing was applied to each image:
* Auto-orientation of pixel data (with EXIF-orientation stripping)
* Resize to 512x512 (Stretch)

The following augmentation was applied to create 3 versions of each source image:
* 50% probability of horizontal flip
* 50% probability of vertical flip
* Random brigthness adjustment of between -60 and +60 percent
* Random Gaussian blur of between 0 and 3.25 pixels

The following transformations were applied to the bounding boxes of each image:
* Random rotation of between -15 and +15 degrees


