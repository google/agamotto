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

import yaml
from yaml.loader import SafeLoader
from utils.logger import logger

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
    