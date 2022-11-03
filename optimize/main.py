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
from config.read_from_yaml import read_from_yaml 
from config.big_query import BigQuery
from config.cloud_storage import CloudStorage
from config.spreadsheet import Spreadsheet
from ads.campaign import Campaign
from utils.logger import logger


class Agamotto:
    def __init__(self):
        config = read_from_yaml()

        cloud_storage = CloudStorage(config=config)
        cloud_storage_deltas = cloud_storage.process_deltas()

        #bigquery = BigQuery(config=config)
        #bigquery.init_database()
        #bigquery_deltas = bigquery.get_deltas()

        spreadsheet = Spreadsheet(config=config)
        campaign_map = spreadsheet.process_spreadsheet_configuration()

        campaign = Campaign(config=config)
        campaign.process_campaign_map(campaign_map, cloud_storage_deltas)

if __name__ == '__main__':
    # generate agamotto.yaml during deploy by client input
    Agamotto()