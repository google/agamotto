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

"""Bigquery main module"""

from typing import List
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from utils.logger import logger
from model.agamotto_model import AgamottoEntry, get_schema


class BigQuery:
    """Bigquery class"""

    def __init__(self, config):
        self._bigquery_service = None
        self._gcp_project = config["gcp"]["project"]
        self._gcp_dataset = config["gcp"]["dataset"]
        self._gcp_bigquery_table = config["gcp"]["bigquery_table"]
        self._location_latlong = config["location"]["latlong"]
        self._location_id = config["location"]["id"]
        self._location_name = config["location"]["name"]
        self._table_id = (
            f"{self._gcp_project}.{self._gcp_dataset}.{self._gcp_bigquery_table}"
        )

    def _get_bigquery_service(self):
        """Fetch bigquery service if it does not exists

        Raises:
            ex: #TODO

        Returns:
            #TODO: _description_
        """
        if not self._bigquery_service:
            try:
                self._bigquery_service = bigquery.Client()
            except Exception as ex:
                raise ex
        return self._bigquery_service

    def create_count_table(self):
        """Create the count table if bigquery save is enabled"""
        try:
            self._bigquery_service = bigquery.Client()
            if self._bigquery_service.get_table(self._table_id):
                logger(self.__class__.__name__).info(
                    f"Table {self._table_id} already exists"
                )
        except NotFound:
            # CreateModel
            table = bigquery.Table(self._table_id, schema=get_schema())
            table = self._bigquery_service.create_table(table)
            logger(self.__class__.__name__).info(
                f"Created table {table.project}.{table.dataset_id}.{table.table_id}".format()
            )

    def insert(self, count_list: List[int]):
        """Insert a list of counts into count_table

        Args:
            count_list (List[int]): #TODO

        Raises:
            ex: #TODO
        """
        try:
            rows = []
            for count, day_time in count_list:
                entry = AgamottoEntry(
                    count=count,
                    day_time=day_time,
                    latlong=self._location_latlong,
                    location_id=self._location_id,
                    location_name=self._location_name,
                ).__dict__
                rows.append(entry)
            errors = self._get_bigquery_service().insert_rows_json(self._table_id, rows)
            if errors == []:
                logger(self.__class__.__name__).info("Stream insert was successfull")
            else:
                logger(self.__class__.__name__).info(
                    f"Encountered errors while inserting rows: {errors}"
                )
        except Exception as ex:
            raise ex
