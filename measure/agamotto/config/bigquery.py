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
    #
    # Satisfy if every condition to get service is OK
    #
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

    def read_sql(self, path):
        sql_file = None
        with open(path, 'r') as file:
            sql_file = file.read()
        return sql_file
    
    def init_database(self):
        try:
            self._bigquery_service = bigquery.Client()
            logger(self.__class__.__name__).info("Attempting to create Bigquery Tables: sales_visits")
            if(self._bigquery_service.query(get_agamotto_sales_visits_query(self._config['gcloud_read_project'], self._config['gcloud_read_dataset']), location=self._config['gcloud_bq_location']).result()):
                logger(self.__class__.__name__).info("Table sales_visits was created successfully")
                logger(self.__class__.__name__).info("Attempting to create Bigquery Tables: agamotto_deltas")
                if(self._bigquery_service.query(get_agamotto_deltas_query(self._config['gcloud_read_project'], self._config['gcloud_read_dataset']), location=self._config['gcloud_bq_location']).result()):
                    logger(self.__class__.__name__).info("Table agamotto_deltas was created successfully")
        except Exception as ex:
            logger(self.__class__.__name__).info("Table agamotto_deltas was created successfully")
            raise ex

    def execute_query(self, query):
        return self._get_bigquery_service().query(query)

    def process_deltas(self, deltas):
        result = {}
        try:
            for row in deltas:
                delta_sales_wow_percentage = row['delta_sales_wow_percentage']
                delta_count_wow_percentage = row['delta_count_wow_percentage']
                store_id = row['store_id']
                deltas_dict = dict({row['store_id']: [row['delta_sales_wow_percentage'], row['delta_count_wow_percentage']]})
                result.update(deltas_dict)
            logger(self.__class__.__name__).info("Number of deltas found: " + str(len(result)))
            return result
        except Exception as ex:
            raise ex
        

    def get_deltas(self):
        #
        # Externalize it and change to gcloud_write_dataset
        #
        logger(self.__class__.__name__).info("Reading table agamotto_deltas...")
        query = """
            SELECT * FROM `{project}.{dataset}.agamotto_deltas`
        """.format(project=self._config['gcloud_read_project'], dataset=self._config['gcloud_read_dataset'])
        deltas = self.execute_query(query)
        return self.process_deltas(deltas=deltas)

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
            table_id = "yagamotto-robsantos.agamotto-measure.agamotto_count"

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