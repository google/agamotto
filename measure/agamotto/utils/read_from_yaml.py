# import pyyaml module
import yaml
from yaml.loader import SafeLoader
from utils.logger import logger

# Open the file and load the file

def read_from_yaml(file_name = "agamotto.yaml"):
    logger().info("Attempting to read YAML: agamotto.yaml")
    try:
        with open(file_name) as f:
            data = yaml.load(f, Loader=SafeLoader)
        logger().debug("Read yaml with data: "+ str(data))
        return data
    except Exception as ex:
        logger().error("Error when attempting to read yaml: " + str(ex))
        raise ex
    