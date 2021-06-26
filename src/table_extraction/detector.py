#!/usr/bin/env python3

# MIT License

# Copyright (c) 2018 The University of Michigan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys

def get_parent_dir(n=1):
#returns the n-th parent dicrectory of the current working directory
    current_path = os.path.dirname(os.path.abspath(__file__))
    for k in range(n):
        current_path = os.path.dirname(current_path)
    return current_path

#src_path = os.path.join(get_parent_dir(1), "2_Training", "src")
#utils_path = os.path.join(get_parent_dir(1), "Utils")
#sys.path.append(src_path)
#sys.path.append(utils_path)
yolo_path = os.path.join(os.path.dirname(__file__),'yolo_helpers','keras_yolo3')
sys.path.insert(1, yolo_path)
import argparse
from yolo_helpers.keras_yolo3.yolo import YOLO, detect_video
from yolo import YOLO, detect_video
from PIL import Image
from timeit import default_timer as timer
from yolo_helpers.utils import load_extractor_model, load_features, parse_input, detect_object
import test
import yolo_helpers.utils
import pandas as pd
import numpy as np
from yolo_helpers.get_file_paths import GetFileList
import random

def detect_func(input_paths, output_path, model_path,classes_path,anchors_path):
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

    # Split images and videos
    img_endings = (".jpg", ".jpg", ".png")
    input_paths = GetFileList(input_paths)
    input_image_paths = []
    for item in input_paths:
        if item.endswith(img_endings):
            input_image_paths.append(item)
    if not os.path.exists(output_path):
         os.makedirs(output_path)


    # define YOLO detector
    yolo = YOLO(
        **{
            "model_path": model_path,
            "anchors_path": anchors_path,
            "classes_path": classes_path,
            "score": 0.25,
            "gpu_num": 1,
            "model_image_size": (416, 416),
        }
    )
    # Make a dataframe for the prediction outputs
    out_df = pd.DataFrame(
        columns=[
            "image",
            "image_path",
            "xmin",
            "ymin",
            "xmax",
            "ymax",
            "label",
            "confidence",
            "x_size",
            "y_size",
        ]
    )
    # labels to draw on images
    class_file = open(classes_path, "r")
    input_labels = [line.rstrip("\n") for line in class_file.readlines()]
    print("Found {} input labels: {} ...".format(len(input_labels), input_labels))
    if input_image_paths:
        print(
            "Found {} input images: {} ...".format(
                len(input_image_paths),
                [os.path.basename(f) for f in input_image_paths[:5]],
            )
        )
        start = timer()
        text_out = ""

        # This is for images
        for i, img_path in enumerate(input_image_paths):
            print(img_path)
            prediction, image = detect_object(
                yolo,
                img_path,
                save_img=False,
                save_img_path=output_path,
                postfix="table",
            )
            y_size, x_size, _ = np.array(image).shape
            for single_prediction in prediction:
                out_df = out_df.append(
                    pd.DataFrame(
                        [
                            [
                                os.path.basename(img_path.rstrip("\n")),
                                img_path.rstrip("\n"),
                            ]
                            + single_prediction
                            + [x_size, y_size]
                        ],
                        columns=[
                            "image",
                            "image_path",
                            "xmin",
                            "ymin",
                            "xmax",
                            "ymax",
                            "label",
                            "confidence",
                            "x_size",
                            "y_size",
                        ],
                    )
                )
        end = timer()
        print(
            "Processed {} images in {:.1f}sec - {:.1f}FPS".format(
                len(input_image_paths),
                end - start,
                len(input_image_paths) / (end - start),
            )
        )
        out_df.to_csv("Detection_Results.csv", index=False)
    # Close the current yolo session
    yolo.close_session()
if __name__=="__main__":
    import os
    import sys
    import cv2
    import time
    import csv


    def get_parent_dir(n=1):
        """ returns the n-th parent dicrectory of the current
        working directory """
        current_path = os.path.dirname(os.path.abspath(__file__))
        for k in range(n):
            current_path = os.path.dirname(current_path)
        return current_path

    import argparse
    from yolo_helpers.keras_yolo3.yolo import YOLO, detect_video
    from PIL import Image
    from timeit import default_timer as timer
    from yolo_helpers.utils import load_extractor_model, load_features, parse_input, detect_object
    import test
    import yolo_helpers.utils
    import pandas as pd
    import numpy as np
    from yolo_helpers.get_file_paths import GetFileList
    import random

    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

    # Set up folder names for default values
    root = os.path.join(os.getcwd(),"../../src/table_extraction")
    image_test_folder = os.path.join(root, "TempPDF")

    detection_results_file = os.path.join(root, "Detection_Results.csv")


    model_classes = os.path.join(root, "yolo_helpers","data_classes.txt")

    anchors_path = os.path.join(root,"yolo_helpers", "keras_yolo3", "model_data", "yolo_anchors.txt")

    FLAGS = None


    if __name__ == "__main__":


        parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)

        parser.add_argument(
            "--input_path",
            type=str,
            default=image_test_folder,
            help="Path to image/video directory. All subdirectories will be included. Default is "
            + image_test_folder,
        )


        parser.add_argument(
            "--file_types",
            "--names-list",
            nargs="*",
            default=[],
            help="Specify list of file types to include. Default is --file_types .jpg .jpeg .png .mp4",
        )

        parser.add_argument(
            "--yolo_model",
            type=str,
            dest="model_path",
            default=os.getcwd(),
            help="Path to pre-trained weight files. Default is " +os.getcwd(),
        )

        parser.add_argument(
            "--anchors",
            type=str,
            dest="anchors_path",
            default=anchors_path,
            help="Path to YOLO anchors. Default is " + anchors_path,
        )

        parser.add_argument(
            "--classes",
            type=str,
            dest="classes_path",
            default=model_classes,
            help="Path to YOLO class specifications. Default is " + model_classes,
        )

        parser.add_argument(
            "--gpu_num", type=int, default=1, help="Number of GPU to use. Default is 1"
        )

        parser.add_argument(
            "--confidence",
            type=float,
            dest="score",
            default=0.25,
            help="Threshold for YOLO object confidence score to show predictions. Default is 0.25.",
        )

        parser.add_argument(
            "--box_file",
            type=str,
            dest="box",
            default=detection_results_file,
            help="File to save bounding box results to. Default is "
            + detection_results_file,
        )


        FLAGS = parser.parse_args()

        file_types = FLAGS.file_types

        if file_types:
            input_paths = GetFileList(FLAGS.input_path, endings=file_types)
        else:
            input_paths = GetFileList(FLAGS.input_path)

        # Split images and videos
        img_endings = (".jpg", ".jpg", ".png")
        vid_endings = (".mp4", ".mpeg", ".mpg", ".avi")

        input_image_paths = []
        input_video_paths = []
        for item in input_paths:
            if item.endswith(img_endings):
                input_image_paths.append(item)
            elif item.endswith(vid_endings):
                input_video_paths.append(item)

        # define YOLO detector

        yolo = YOLO(
            **{
                "model_path": FLAGS.model_path,
                "anchors_path": FLAGS.anchors_path,
                "classes_path": FLAGS.classes_path,
                "score": FLAGS.score,
                "gpu_num": FLAGS.gpu_num,
                "model_image_size": (416, 416),
            }
        )

        # Make a dataframe for the prediction outputs
        out_df = pd.DataFrame(
            columns=[
                "image",
                "image_path",
                "xmin",
                "ymin",
                "xmax",
                "ymax",
                "label",
                "confidence",
                "x_size",
                "y_size",
            ]
        )

        # labels to draw on images
        class_file = open(FLAGS.classes_path, "r")
        input_labels = [line.rstrip("\n") for line in class_file.readlines()]
        print("Found {} input labels: {} ...".format(len(input_labels), input_labels))

        if input_image_paths:
            print(
                "Found {} input images: {} ...".format(
                    len(input_image_paths),
                    [os.path.basename(f) for f in input_image_paths[:5]],
                )
            )
            start = timer()
            text_out = ""

            # This is for images
            for i, img_path in enumerate(input_image_paths):
                print(img_path)
                prediction, image = detect_object(
                    yolo,
                    img_path,
                    save_img=False,
                    save_img_path=os.getcwd(),
                    postfix="",
                )
                #print(prediction)
                y_size, x_size, _ = np.array(image).shape
                for single_prediction in prediction:
                    out_df = out_df.append(
                        pd.DataFrame(
                            [
                                [
                                    os.path.basename(img_path.rstrip("\n")),
                                    img_path.rstrip("\n"),
                                ]
                                + single_prediction
                                + [x_size, y_size]
                            ],
                            columns=[
                                "image",
                                "image_path",
                                "xmin",
                                "ymin",
                                "xmax",
                                "ymax",
                                "label",
                                "confidence",
                                "x_size",
                                "y_size",
                            ],
                        )
                    )
            end = timer()
            print(
                "Processed {} images in {:.1f}sec - {:.1f}FPS".format(
                    len(input_image_paths),
                    end - start,
                    len(input_image_paths) / (end - start),
                )
            )
            out_df.to_csv(FLAGS.box, index=False)

        # This is for videos
        if input_video_paths:
            print(
                "Found {} input videos: {} ...".format(
                    len(input_video_paths),
                    [os.path.basename(f) for f in input_video_paths[:5]],
                )
            )
            start = timer()
            for i, vid_path in enumerate(input_video_paths):
                output_path = os.path.join(
                    os.getcwd(),
                    os.path.basename(vid_path).replace(".", "" + "."),
                )
                detect_video(yolo, vid_path, output_path=output_path)

            end = timer()
            print(
                "Processed {} videos in {:.1f}sec".format(
                    len(input_video_paths), end - start
                )
            )
        # Close the current yolo session
        yolo.close_session()