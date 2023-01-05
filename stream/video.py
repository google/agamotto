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

import cv2

input_list = ["input_videos/fastshop_recording.mov", "input_videos/shopping_2.mp4", "input_videos/shopping_3.mp4"]


class Video(object):
    def __init__(self):
       self.counter = 0
       self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, frame = self.video.read()
        if frame is None:
            self.counter += 1
            if self.counter == 3:
                self.counter = 0
            self.video = cv2.VideoCapture(0)
            ret, frame = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()