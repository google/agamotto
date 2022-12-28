# Copyright 2022 Google Inc.
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

# limitations under the License.
import os
import zipfile
from tensorflow import keras
import tensorflow as tf
import tensorflow_datasets as tfds
from retinanet.labelencoder import LabelEncoder
from retinanet.retinanet import RetinaNet, RetinaNetLoss, get_backbone
from retinanet.autotune import apply_autotune
from retinanet.decodepredictions import DecodePredictions
from retinanet.utils import read_image, read_video
from retinanet.preprocess import preprocess_data

class Agamotto():
    def __init__(self, config):
        """
        Download weights - Non-training
        """
        url = "https://github.com/srihari-humbarwadi/datasets/releases/download/v0.1.0/data.zip"
        filename = os.path.join(os.getcwd(), "data.zip")
        keras.utils.get_file(filename, url)

        with zipfile.ZipFile("data.zip", "r") as z_fp:
            z_fp.extractall("./")
        

        self.set_parameters()
        self.init_model()
        self.load_dataset()        
        #self.autotune_train()
        self.load_weights()
        self.build_inference_model()
    


    """
    ## Setting parameters
    """
    def set_parameters(self):
        self._model_dir = "newretina/"
        self._label_encoder = LabelEncoder()

        self._num_classes = 80
        self._batch_size = 1

        self._learning_rates = [2.5e-06, 0.000625, 0.00125, 0.0025, 0.00025, 2.5e-05]
        self._learning_rate_boundaries = [125, 250, 500, 240000, 360000]
        self._learning_rate_fn = tf.optimizers.schedules.PiecewiseConstantDecay(
            boundaries=self._learning_rate_boundaries, values=self._learning_rates
        )

    """
    ## Initialize Model
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
                filepath=os.path.join(self._model_dir, "weights" + "_epoch_{epoch}"),
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
        optimizer = tf.optimizers.SGD(learning_rate=self._learning_rate_fn, momentum=0.9)
        self._model.compile(loss=loss_fn, optimizer=optimizer)
    
    """
    ## Train and autotune
    """
    def autotune_train(self):
        self.compile_model()
        self.set_callbacks()
        self._train_dataset, self._val_dataset = apply_autotune(train_dataset=self._train_dataset, val_dataset=self._val_dataset, batch_size=self._batch_size, label_encoder=self._label_encoder) 
        epochs = 1
        self._model.fit(
            self._train_dataset.take(50),
            validation_data=self._val_dataset.take(20),
            epochs=epochs,
            callbacks=self._callbacks_list,
            verbose=1,
        )
    
    """
    ## Load the COCO2017 dataset using TensorFlow Datasets
    """
    def load_dataset(self):
        #  set `data_dir=None` to load the complete dataset
        (self._train_dataset, self._val_dataset), self._dataset_info = tfds.load(
                "coco/2017", split=["train", "validation"], with_info=True, data_dir="data"
        )
        self.int2str = self._dataset_info.features["objects"]["label"].int2str

    """
    ## Loading weights
    """
    def load_weights(self):
        # Change this to `model_dir` when not using the downloaded weights
        weights_dir = "data"
        latest_checkpoint = tf.train.latest_checkpoint(weights_dir)
        self._model.load_weights(latest_checkpoint)

    """
    ## Building inference model
    """
    def build_inference_model(self):
        image = tf.keras.Input(shape=[None, None, 3], name="image")
        predictions = self._model(image, training=False)
        detections = DecodePredictions(confidence_threshold=0.30)(image, predictions)
        self._inference_model = tf.keras.Model(inputs=image, outputs=detections)

    def process_video(self, video_path):
        read_video(video_path=video_path, inference_model=self._inference_model, int2str=self.int2str)
    
    def process_stream(self, stream_path):
        read_video(video_path=stream_path, inference_model=self._inference_model, int2str=self.int2str)

    def process_image(self, image_path):
        read_image(image_path=image_path, inference_model=self._inference_model, int2str=self.int2str)

