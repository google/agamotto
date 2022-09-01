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
from agamotto import Agamotto

app = Flask(__name__)

agamotto = None

@app.route('/metrics')
def metrics():
    count = agamotto.retrieve_data()
    return 'person_store_count{store="store_1", camera="cam_1"} %s' % count

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_count')
def get_count():
    return str(agamotto.retrieve_data())

if __name__ == '__main__':
    agamotto = Agamotto()
    app.run(host='0.0.0.0',port='9097', debug=True)