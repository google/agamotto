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


from flask import Flask, render_template, Response
from video import Video

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

def gen(video):
    while True:
        frame = video.get_frame()
        yield (b'--frame\r\n'
       b'Content-Type:image/jpeg\r\n'
       b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n'
       b'\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
        return Response(gen(Video()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='9098', debug=True)