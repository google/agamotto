from google.cloud import bigquery
from sql.init_database import get_agamotto_deltas_query, get_agamotto_sales_visits_query
from utils.logger import logger

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