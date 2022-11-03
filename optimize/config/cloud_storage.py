from google.cloud import storage
from utils.logger import logger
from google.oauth2.credentials import Credentials
import dask.dataframe as dd
import csv


class CloudStorage:
    def __init__(self, config):
        self._storage_client = storage.Client()
        self._config = config
        self._bucket_name = config['agamotto-bucket']
        self._file = self.list_blobs(f"{self._bucket_name}")
        
    def process_deltas(self):
        result = {}
        storage_client = storage.Client()
        bucket = storage_client.bucket(self._bucket_name)
        blob = bucket.blob(self._file.name)

        try:
            with blob.open("r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    deltas_dict = dict({row['store_id']: [row['delta_sales_wow_percentage']]})
                    result.update(deltas_dict)
            logger(self.__class__.__name__).info("Number of deltas found: " + str(result))
            logger(self.__class__.__name__).info("Number of deltas found: " + str(len(result)))
            
            return result
        except Exception as ex:
            raise ex


        
    ## def write(self,bucket_name, blob_name):
    ##     """Write and read a blob from GCS using file-like IO"""
## 
    ##     storage_client = storage.Client()
    ##     bucket = storage_client.bucket(bucket_name)
    ##     blob = bucket.blob(blob_name)
## 
    ##     with blob.open("w") as f:
    ##         f.write("Hello world")
## 
    ## def read_fsf(self, blob_name):
    ##     """Write and read a blob from GCS using file-like IO"""
## 
    ##     storage_client = storage.Client()
    ##     bucket = storage_client.bucket(self._bucket_name)
    ##     blob = bucket.blob(blob_name.name)
## 
    ##     with blob.open("r") as f:
    ##         reader = csv.DictReader(f)
    ##         for row in reader:
    ##             print(row)


    def list_blobs(self, bucket_name):
        """Lists all the blobs in the bucket."""
        # bucket_name = "your-bucket-name"

        # Note: Client.list_blobs requires at least package version 1.17.0.
        blobs = self._storage_client.list_blobs(bucket_name)
        for blob in blobs:
            return blob

    ## def delete_blob(bucket_name, blob_name):
    ##     """Deletes a blob from the bucket."""
    ##     # bucket_name = "your-bucket-name"
    ##     # blob_name = "your-object-name"
## 
    ##     storage_client = storage.Client()
## 
    ##     bucket = storage_client.bucket(bucket_name)
    ##     blob = bucket.blob(blob_name)
    ##     blob.delete()
## 
    ##     print(f"Blob {blob_name} deleted.")
