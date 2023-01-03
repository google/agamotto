from google.cloud import bigquery
from datetime import datetime


class AgamottoEntry:
    """Model Class that represents an entry that needs to be updated."""

    def __init__(self, count: int, day_time: datetime, latlong: str, location_id: int, location_name: str):
        self.count = int(count)
        self.day_time = day_time
        self.latlong = latlong
        self.location_id = int(location_id)
        self.location_name = location_name

def get_schema():
    schema = [
        bigquery.SchemaField("count", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("day_time", "DATETIME", mode="REQUIRED"),
        bigquery.SchemaField("latlong", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("location_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("location_name", "STRING", mode="REQUIRED"),
    ]
    return schema