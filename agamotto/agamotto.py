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

import torch
import cv2

class Agamotto():
    def __init__(self):
        self.model = self.load_model()
        self.model.conf = 0.33
        self.model.iou = 0.33 
        self.model.classes = [0] 
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.player = self.get_video()

    def get_video(self):
        cap = cv2.VideoCapture("http://stream:9098/video_feed")
        assert cap is not None
        return cap

    def load_model(self):
        model = torch.hub.load('ultralytics/yolov5', 'custom', path="weights/crowdhuman_yolov5m.pt")
        return model

    def score_frame(self, frame):
        self.model.to(self.device)
        results = self.model([frame])
        labels, cord = results.xyxyn[0][:, -1].to('cpu').numpy(), results.xyxyn[0][:, :-1].to('cpu').numpy()
        return labels, cord

    def get_count(self, results):
        labels, cord = results
        count = len(labels)
        return count

    def retrieve_data(self):
        assert self.player.isOpened()
        ret, frame = self.player.read()
        results = self.score_frame(frame)
        count = self.get_count(results)
        return count



