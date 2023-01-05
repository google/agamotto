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
from config.bigquery import BigQuery
from utils.read_from_yaml import read_from_yaml
from agamotto.agamotto import Agamotto
import os

if __name__ == '__main__':

    
    config = read_from_yaml()

    os.environ['TZ'] = config['timezone']
    
    if config["gcp"]["save_to_bigquery"]:
        bigquery = BigQuery(config)
        bigquery.create_count_table()
    
    agamotto = Agamotto(config)
    agamotto.process_media(config["video"]["input_location"])

