from google.cloud import bigquery
from utils.logger import logger
from google.cloud.exceptions import NotFound

# https://codelabs.developers.google.com/codelabs/cloud-bigquery-python#6
# 
# export PROJECT_ID=$(gcloud config get-value core/project)
# 
# gcloud iam service-accounts create agamotto-bigquery-sa --display-name "Agamotto service account"
# 
# gcloud iam service-accounts keys create ~/key.json --iam-account agamotto-bigquery-sa@${PROJECT_ID}.iam.gserviceaccount.com
# 
# export GOOGLE_APPLICATION_CREDENTIALS=~/key.json
#
#
# gcloud projects add-iam-policy-binding ${PROJECT_ID} --member "serviceAccount:agamotto-bigquery-sa@${PROJECT_ID}.iam.gserviceaccount.com" --role "roles/bigquery.user"
#
# gcloud projects get-iam-policy $PROJECT_ID
#
# Local deploy
# gcloud auth application-default login (/Users/robsantos/.config/gcloud/application_default_credentials.json)
#
# gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/bigquery
#
# gcloud config set project google.com:robsantos-agamotto


class BigQuery:
    def __init__(self, config):
        self._bigquery_service = None
        self._config = config

        
    def _get_bigquery_service(self):
        if not self._bigquery_service:
            try:
                self._bigquery_service = bigquery.Client()
            except Exception as ex:
                raise ex
        return self._bigquery_service

    def execute_query(self, query):
        return self._get_bigquery_service().query(query)

    def create_count_table(self):
        try:
            self._bigquery_service = bigquery.Client()
            table_id = "google.com:robsantos-agamotto.agamotto_measure.agamotto_count"
            if self._bigquery_service.get_table(table_id):
                logger(self.__class__.__name__).info(f"Table {table_id} already exists")
        except NotFound:
            # CreateModel
            schema = [
                bigquery.SchemaField("count", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("day", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("time", "TIME", mode="REQUIRED"),
                bigquery.SchemaField("latlong", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("location_id", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("location_name", "STRING", mode="REQUIRED"),
            ]
            table = bigquery.Table(table_id, schema=schema)
            table = self._bigquery_service.create_table(table) 
            logger(self.__class__.__name__).info("Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))
    
    def insert_row(self, count):
        # Create Model
        self._bigquery_service = bigquery.Client()
        self._bigquery_service.query(f"INSERT INTO `google.com:robsantos-agamotto.agamotto_measure.agamotto_count` VALUES ({count}, CURRENT_DATE(), CURRENT_TIME(), '-1452.254,-2158.25', 25, 'Loja Paulista')")
            

    def insert(self):
        try:
            # Construct a BigQuery client object.
            client = bigquery.Client()

            # TODO(developer): Set table_id to the ID of table to append to.
            table_id = "agamotto-robsantos.agamotto-measure.agamotto_count"

            rows_to_insert = [
                {"full_name": "Phred Phlyntstone", "age": 32},
                {"full_name": "Wylma Phlyntstone", "age": 29},
            ]

            errors = client.insert_rows_json(table_id, rows_to_insert)  # Make an API request.
            if errors == []:
                print("New rows have been added.")
            else:
                print("Encountered errors while inserting rows: {}".format(errors))
        except Exception as ex:
            raise ex