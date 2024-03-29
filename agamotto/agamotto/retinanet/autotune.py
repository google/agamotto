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

import tensorflow as tf
from .preprocess import preprocess_data


def apply_autotune(train_dataset, val_dataset, batch_size, label_encoder):
    """Setting up a tf.data pipeline
    To ensure that the model is fed with data efficiently we will be using
    `tf.data` API to create our input pipeline. The input pipeline
    consists for the following major processing steps:
    - Apply the preprocessing function to the samples
    - Create batches with fixed batch size. Since images in the batch can
    have different dimensions, and can also have different number of
    objects, we use `padded_batch` to the add the necessary padding to create
    rectangular tensors
    - Create targets for each sample in the batch using `LabelEncoder`

        Args:
            train_dataset (#TODO): _description_
            val_dataset (#TODO): _description_
            batch_size (#TODO): _description_
            label_encoder (#TODO): _description_

        Returns:
            #TODO: _description_
    """
    autotune = tf.data.AUTOTUNE
    train_dataset = train_dataset.map(preprocess_data, num_parallel_calls=autotune)
    train_dataset = train_dataset.shuffle(8 * batch_size)
    train_dataset = train_dataset.padded_batch(
        batch_size=batch_size, padding_values=(0.0, 1e-8, -1), drop_remainder=True
    )
    train_dataset = train_dataset.map(
        label_encoder.encode_batch, num_parallel_calls=autotune
    )
    train_dataset = train_dataset.apply(tf.data.experimental.ignore_errors())
    train_dataset = train_dataset.prefetch(autotune)

    val_dataset = val_dataset.map(preprocess_data, num_parallel_calls=autotune)
    val_dataset = val_dataset.padded_batch(
        batch_size=1, padding_values=(0.0, 1e-8, -1), drop_remainder=True
    )
    val_dataset = val_dataset.map(
        label_encoder.encode_batch, num_parallel_calls=autotune
    )
    val_dataset = val_dataset.apply(tf.data.experimental.ignore_errors())
    val_dataset = val_dataset.prefetch(autotune)

    return train_dataset, val_dataset
