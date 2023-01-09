# Copyright 2023 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
#
# limitations under the License.

import os
import zipfile
import time
import cv2
from tensorflow import keras
import tensorflow as tf
import tensorflow_datasets as tfds
from .retinanet.labelencoder import LabelEncoder
from .retinanet.retinanet import RetinaNet, RetinaNetLoss, get_backbone
from .retinanet.autotune import apply_autotune
from .retinanet.decodepredictions import DecodePredictions
from .retinanet.utils import read_image, prepare_image
from .retinanet.preprocess import preprocess_data
from datetime import datetime, timezone
from config.bigquery import BigQuery
from utils.logger import logger


class Agamotto():
    """
    Agamotto's main class, here it access retinanet folder
    then download, train and fit the model based on a input in agamotto.yaml

    #TODO:
    - decouple midia methods
    - decouple model methods
    - create a agnostic class related to any model
    """
    def __init__(self, config):
        """
        The constructor receives the parameters and initialize methods,
        if model.train is True, then the autotune_train is called
        """

        self._config = config
        self.set_parameters()
        self.download_weights()
        self.init_model()
        self.load_dataset()
        if self._config["model"]["train"]:
            self.autotune_train()
        self.load_weights()
        self.build_inference_model()

    def download_weights(self):
        """
        Downloading weights for first (or only) executions, it will download, extract and create
        a folder based on agamotto.yaml file.
        #TODO Improvements:
            - Add a download weights URL inside agamotto.yaml
            - Add a version inside agamotto.yaml
        """
        url = "https://github.com/roberto-goncalves/datasets/releases/download/v0/{}.zip".format(self._load_weights_dir)
        filename = os.path.join(os.getcwd(), "{}.zip".format(self._load_weights_dir))
        keras.utils.get_file(filename, url)
        with zipfile.ZipFile("{}.zip".format(self._load_weights_dir), "r") as z_fp:
            z_fp.extractall("./")

    def set_parameters(self):
        """
        Set parameters acts as a constructor for model parameters
        """
        self._save_weights_dir = self._config["model"]["save_weights_dir"]
        self._label_encoder = LabelEncoder()

        self._num_classes = self._config["model"]["num_classes"]
        self._batch_size = self._config["model"]["batch_size"]
        self._confidence_threshold = self._config["model"]["confidence_threshold"]
        # Change this to `model_dir` when not using the downloaded weights
        self._load_weights_dir = self._config["model"]["load_weights_dir"]
        self._train_dataset_size = self._config["model"]["train_dataset_size"]
        self._val_dataset_size = self._config["model"]["val_dataset_size"]
        self._epochs = self._config["model"]["epochs"]
        self._model_optimizer_momentum = self._config["model"]["model_optimizer_momentum"]
        self._tensorflow_dataset = self._config["model"]["tensorflow_dataset"]

        self._datadir = None if self._config["model"]["load_dataset"] else self._load_weights_dir

        self._video_write_output_fps = self._config["video"]["write_output_fps"]
        self._video_read_inverval = self._config["video"]["read_interval"]
        self._video_output_location = self._config["video"]["output_location"]
        self._video_is_stream = self._config["video"]["is_stream"]

        self._gcp_save_to_bigquery = self._config["gcp"]["save_to_bigquery"]


        self._learning_rates = [2.5e-06, 0.000625, 0.00125, 0.0025, 0.00025, 2.5e-05]
        self._learning_rate_boundaries = [125, 250, 500, 240000, 360000]
        self._learning_rate_fn = tf.optimizers.schedules.PiecewiseConstantDecay(
            boundaries=self._learning_rate_boundaries, values=self._learning_rates
        )

    """
    Init model actually instantiate the Retinanet constructor and add the backbone
    """
    def init_model(self):
        resnet50_backbone = get_backbone()
        self._model = RetinaNet(self._num_classes, resnet50_backbone)


    """
    ## Setting up callbacks
    """
    def set_callbacks(self):
        self._callbacks_list = [
            tf.keras.callbacks.ModelCheckpoint(
                filepath=os.path.join(self._save_weights_dir, "weights" + "_epoch_{epoch}"),
                monitor="loss",
                save_best_only=False,
                save_weights_only=True,
                verbose=1,
            )
        ]

    """
    ## Compile Model
    """
    def compile_model(self):
        loss_fn = RetinaNetLoss(self._num_classes)
        optimizer = tf.optimizers.SGD(learning_rate=self._learning_rate_fn,
                        momentum=self._model_optimizer_momentum)
        self._model.compile(loss=loss_fn, optimizer=optimizer)

    """
    ## Train and autotune
    """
    def autotune_train(self):
        self.compile_model()
        self.set_callbacks()
        self._train_dataset, self._val_dataset = apply_autotune(train_dataset=self._train_dataset,
            val_dataset=self._val_dataset,
            batch_size=self._batch_size,
            label_encoder=self._label_encoder)
        self._model.fit(
            self._train_dataset.take(self._train_dataset_size),
            validation_data=self._val_dataset.take(self._val_dataset_size),
            epochs=self._epochs,
            callbacks=self._callbacks_list,
            verbose=1,
        )

    """
    ## Load the COCO2017 dataset using TensorFlow Datasets
    """
    def load_dataset(self):
        (self._train_dataset, self._val_dataset), self._dataset_info = tfds.load(
            self._tensorflow_dataset,
            split=["train", "validation"],
            with_info=True,
            data_dir=self._datadir
        )
        self._int2str = self._dataset_info.features["objects"]["label"].int2str

    """
    ## Loading weights
    """
    def load_weights(self):
        latest_checkpoint = tf.train.latest_checkpoint(self._load_weights_dir)
        self._model.load_weights(latest_checkpoint)

    """
    ## Building inference model
    """
    def build_inference_model(self):
        image = tf.keras.Input(shape=[None, None, 3], name="image")
        predictions = self._model(image, training=False)
        detections = DecodePredictions(
            confidence_threshold=self._confidence_threshold)(image, predictions)
        self._inference_model = tf.keras.Model(inputs=image, outputs=detections)


    def process_media(self, path):
        if self._video_is_stream:
            self.process_stream(path)
        else:
            self.process_video(path)

    def process_video(self, video_path):
        player = cv2.VideoCapture(video_path)
        frame_width = int(player.get(3))
        frame_height = int(player.get(4))
        logger(self.__class__.__name__).info("Loading video {}".format(video_path))
        output = cv2.VideoWriter(self._video_output_location,
            cv2.VideoWriter_fourcc('M','J','P','G'),
            self._video_write_output_fps,
            (frame_width,frame_height))
        count = 0
        detections_count = []
        while player.isOpened():
            ret, frame = player.read()
            if not ret:
                logger(self.__class__.__name__).info("Frame was not load correctly, exiting...")
                break
            detections, ratio, num_detections = self.create_detections(frame)
            logger(self.__class__.__name__).info("Count of persons: {}".format(num_detections))
            self.draw_boxes_to_frame(frame=frame,
                detections=detections,
                num_detections=num_detections,
                ratio=ratio)
            detections_count.append(num_detections)
            output.write(frame)
            count += self._video_read_inverval * 30
            player.set(cv2.CAP_PROP_POS_FRAMES, count)
        if self._gcp_save_to_bigquery:
            self.insert_to_bigquery(num_detections=detections_count)
        logger(self.__class__.__name__).info("Saving to file {}".format(self._video_output_location))
        cv2.destroyAllWindows()
        output.release()
        player.release()
    
    def process_stream(self, stream_path):
        while True:
            time.sleep(self._video_read_inverval)
            logger(self.__class__.__name__).info("Loading stream {}".format(stream_path))
            player = cv2.VideoCapture(stream_path)
            while player.isOpened():
                ret, frame = player.read()
                if not ret:     
                    logger(self.__class__.__name__).info("Frame was not load correctly, exiting...")
                    break
                
                detections, ratio, num_detections = self.create_detections(frame)
                logger(self.__class__.__name__).info("Count of persons: {}".format(num_detections))
                self.draw_boxes_to_frame(frame=frame, detections=detections, num_detections=num_detections, ratio=ratio)
                if self._gcp_save_to_bigquery:
                    self.insert_to_bigquery(num_detections=[num_detections])
                cv2.imwrite("frame-0.jpg", frame)
                
                break
            cv2.destroyAllWindows()
            player.release()

    def insert_to_bigquery(self, num_detections):
        bigquery = BigQuery(self._config)
        detections_count = []
        for values in num_detections:
            logger(self.__class__.__name__).info("Adding {} to batch".format([values, datetime.now().strftime("%Y-%m-%dT%H:%M:%S")]))
            detections_count.append([values, datetime.now().strftime("%Y-%m-%dT%H:%M:%S")])
        logger(self.__class__.__name__).info(f"Attempting to stream insert {len(detections_count)} rows into BigQuery...")
        bigquery.insert(detections_count) 

    def create_detections(self, frame):
        image = tf.cast(frame, dtype=tf.float32)
        input_image, ratio = prepare_image(image)
        detections = self._inference_model.predict(input_image)
        num_detections = detections.valid_detections[0]

        return detections, ratio, num_detections


    def draw_boxes_to_frame(self, frame, detections, num_detections, ratio):
        class_names = [self._int2str(int(x)) for x in detections.nmsed_classes[0][:num_detections]]
        for box, _cls, score in zip(detections.nmsed_boxes[0][:num_detections] / ratio, class_names, detections.nmsed_scores[0][:num_detections]):
            text = "{}: {:.2f}".format(_cls, score)
            texttotal = "agamotto_total_count: {:.2f}".format(num_detections)
            x1, y1, x2, y2 = box #w, h = x2 - x1, y2 - y1
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 1)
            cv2.putText(frame, text, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_DUPLEX, 0.6, (36,255,12), 1)
            cv2.putText(frame, texttotal, (100, 100), cv2.FONT_HERSHEY_COMPLEX, 0.9, (36,255,12), 2)

    def process_image(self, image_path):
        read_image(image_path=image_path, inference_model=self._inference_model, int2str=self.int2str)

