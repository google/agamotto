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

"""Model module"""

from datetime import datetime
from google.cloud import bigquery


class AgamottoEntry:
    """""Model Class that represents an entry that needs to be updated.""" ""

    def __init__(
        self,
        count: int,
        day_time: datetime,
        latlong: str,
        location_id: int,
        location_name: str,
    ):
        self.count = int(count)
        self.day_time = day_time
        self.latlong = latlong
        self.location_id = int(location_id)
        self.location_name = location_name


def get_schema():
    """Returns the table schema from bigquery

    #TODO Improvements:
        - Generate the schema based on AgamottoEntry class

    Returns:
        schema: #TODO
    """
    schema = [
        bigquery.SchemaField("count", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("day_time", "DATETIME", mode="REQUIRED"),
        bigquery.SchemaField("latlong", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("location_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("location_name", "STRING", mode="REQUIRED"),
    ]
    return schema
