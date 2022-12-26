#!/usr/bin/env python
# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# python3.7 update_campaign.py --customer_id 1478517099 --campaign_id 16195596449
"""This example updates a campaign.
To get campaigns, run get_campaigns.py.
"""


import argparse
import resource
import sys

from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads import oauth2
from google.api_core import protobuf_helpers
from utils.logger import logger
from enum import Enum

_BUDGET_TEMPORARY_ID = -1

class Operation(Enum):
    INCREASE = "increase"
    DECREASE = "decrease"


class Campaign:

    def __init__(self, config):
        config_dict = {
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'refresh_token': config['refresh_token'],
            'developer_token': config['developer_token'], 
            'login_customer_id': config['ads_mcc_id'],
            'use_proto_plus': True
        }
        self._googleads_client = GoogleAdsClient.load_from_dict(config_dict, version="v11")
        self._config = config

    
    def process_campaign_map(self, map, deltas):
        try:
            for row in map:
                customer_id = row['CustomerId']
                multiplier = row['BudgetMultiplier']
                max_amount = row['BudgetMaxAmount']
                min_amount = row['BudgetMinAmount']
                campaign_id = row['CampaignId']
                store_ids = row['StoreId'].split(',')
                sales_up_threshold = int(row['SalesUpThreshold']) + 100
                sales_down_threshold = 100 - int(row['SalesDownThreshold'])
                mean_group = 0
                
                for id in store_ids[:]:
                    if id in deltas:
                        delta_sales = float(deltas[id][0])
                        mean_group += delta_sales
                        logger(self.__class__.__name__).info(f"Value of delta sales for store: {id} delta: {delta_sales}")
                    else:
                        logger(self.__class__.__name__).info(f"Removing {id}")
                        store_ids.remove(id)
                mean_group = mean_group / len(store_ids)
                logger(self.__class__.__name__).info(f"Value of delta for group: {store_ids} is: {mean_group}")
                if mean_group <= sales_down_threshold:
                    logger(self.__class__.__name__).info(f"Group delta ({mean_group}) is lower than the lower threshold ({sales_down_threshold}), increasing budget")
                    self.update_performance_max_campaign(customer_id,campaign_id, multiplier, max_amount, min_amount, Operation.INCREASE)
                elif mean_group >= sales_up_threshold:
                    logger(self.__class__.__name__).info(f"Group delta ({mean_group}) is greater than the upper threshold ({sales_up_threshold}), decreasing budget") 
                    self.update_performance_max_campaign(customer_id,campaign_id, multiplier, max_amount, min_amount, Operation.DECREASE)
                else:
                    logger(self.__class__.__name__).info(f"Group delta ({mean_group}) is between the lower ({sales_down_threshold}) and upper ({sales_up_threshold}) thresholds, no update needed")
        except Exception as ex:
            raise ex

    def update_campaign_status(self, customer_id, campaign_id, status = "enable"):
        logger(self.__class__.__name__).info("Updating campaign: " + campaign_id)
        campaign_service = self._googleads_client.get_service("CampaignService")
        # Create campaign operation.
        campaign_operation = self._googleads_client.get_type("CampaignOperation")
        campaign = campaign_operation.update

        campaign.resource_name = campaign_service.campaign_path(
            customer_id, campaign_id
        )

        if status == "enable":
            campaign.status = self._googleads_client.enums.CampaignStatusEnum.ENABLED
        elif status == "pause":
            campaign.status = self._googleads_client.enums.CampaignStatusEnum.PAUSED

        campaign.network_settings.target_search_network = False
        # Retrieve a FieldMask for the fields configured in the campaign.
        self._googleads_client.copy_from(
            campaign_operation.update_mask,
            protobuf_helpers.field_mask(None, campaign._pb),
        )

        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        logger(self.__class__.__name__).info(f"Campaign updated for: {campaign_response.results[0].resource_name}")

    def update_performance_max_campaign(self, customer_id, campaign_id , multiplier, max_amount, min_amount, op):
        googleads_service = self._googleads_client.get_service("GoogleAdsService")
        campaign_budget_operation = self.update_campaign_budget_operation(self._googleads_client, customer_id, campaign_id, multiplier, max_amount, min_amount, op)
        if campaign_budget_operation != None:
            logger(self.__class__.__name__).info(f"Campaign updated for: {campaign_budget_operation}")    
            mutate_operations = [campaign_budget_operation]
            response = googleads_service.mutate(customer_id=customer_id, mutate_operations=mutate_operations)
            logger(self.__class__.__name__).info(f"Campaign updated for: {response}")
        else: 
            logger(self.__class__.__name__).info(f"Campaign budget cannot be updated.")
        


    def update_campaign_budget_operation(self, client, customer_id, campaign_id, multiplier, max_amount, min_amount, op):
        """Creates a MutateOperation that creates a new CampaignBudget.
        A temporary ID will be assigned to this campaign budget so that it can be
        referenced by other objects being created in the same Mutate request.
        Args:
            client: an initialized GoogleAdsClient instance.
            customer_id: a client customer ID.
        Returns:
            a MutateOperation that creates a CampaignBudget.
        """
        try:

            ga_service = client.get_service("GoogleAdsService")

            query = f"""        
            SELECT
              campaign.id,
              campaign.name,
              campaign.campaign_budget,
              campaign_budget.amount_micros
            FROM campaign
            where campaign.id = {campaign_id}
            ORDER BY campaign.id  """

            stream = ga_service.search_stream(customer_id=customer_id, query=query)

            for batch in stream:
                for row in batch.results:
                    logger(self.__class__.__name__).info(f"Campaign info {row}")
                    resource_name = row.campaign.campaign_budget
                    actual_budget = float(row.campaign_budget.amount_micros)

            if op == Operation.INCREASE:
                updated_budget = actual_budget + (actual_budget * float(multiplier))
            else:
                updated_budget = actual_budget - (actual_budget * float(multiplier))

            logger(self.__class__.__name__).info(f"Calculated: {min_amount}, {updated_budget}, {max_amount}")

            if float(min_amount) <= updated_budget <= float(max_amount):
                mutate_operation = client.get_type("MutateOperation")
                campaign_budget_operation = mutate_operation.campaign_budget_operation
                campaign_budget = campaign_budget_operation.update
                campaign_budget.amount_micros = updated_budget
                campaign_budget.explicitly_shared = False
                campaign_budget.resource_name = resource_name
                self._googleads_client.copy_from(
                    mutate_operation.campaign_budget_operation.update_mask,
                    protobuf_helpers.field_mask(None, campaign_budget._pb),
                )            
                return mutate_operation
            else:
                logger(self.__class__.__name__).info(f"Proposed budget overlaped: {min_amount}, {updated_budget}, {max_amount}")
                return None
        except Exception as ex:
            raise ex

    def update_campaign_location_group(self, customer_id):
        """Creates a MutateOperation that creates a new CampaignBudget.
        A temporary ID will be assigned to this campaign budget so that it can be
        referenced by other objects being created in the same Mutate request.
        Args:
            client: an initialized GoogleAdsClient instance.
            customer_id: a client customer ID.
        Returns:
            a MutateOperation that creates a CampaignBudget.
        """
        try:
            ga_service = self._googleads_client.get_service("GoogleAdsService")

            #query = f"""SELECT feed_item_set.feed, feed_item_set.display_name, feed_item_set.feed_item_set_id FROM feed_item_set WHERE feed_item_set.display_name = 'Feed Item Set Agamotto'"""

            query = f"""SELECT feed.id from feed where customer.id = '{customer_id}'"""

            stream = ga_service.search_stream(customer_id=customer_id, query=query)

            for batch in stream:
                for row in batch.results:
                    logger(self.__class__.__name__).info(f"Campaign info {row}")
                    #feed_item_set_resource_name = row.feed_item_set.resource_name
                    #feed_resource_name = row.feed_item_set.feed
                    feed_id = row.feed.id

            feed_item_set_service = self._googleads_client.get_service("FeedItemSetService")
            feed_item_set_operation = self._googleads_client.get_type("FeedItemSetOperation")

            feed_item_set = feed_item_set_operation.create
            # feed_item_set.feed = feed_resource_name
            #feed_item_set.resource_name = feed_item_set_resource_name
            feed_resource_name =  self._googleads_client.get_service("FeedService").feed_path(
                customer_id, feed_id
            )
            feed_item_set.feed = feed_resource_name
            feed_item_set.display_name = f"Location Group - Agamotto"

            dynamic_location_set_filter = feed_item_set.dynamic_location_set_filter
            business_name_filter = dynamic_location_set_filter.business_name_filter
            business_name_filter.business_name = 'Own'
            business_name_filter.filter_type = self._googleads_client.enums.FeedItemSetStringFilterTypeEnum.EXACT

            # self._googleads_client.copy_from(
            #     feed_item_set_operation.update_mask,
            #     protobuf_helpers.field_mask(None, feed_item_set._pb),
            # )

            response = feed_item_set_service.mutate_feed_item_sets(
                customer_id=customer_id, operations=[feed_item_set_operation]
            )   

            print(
               "Updated a feed item set with resource name: "
                    f"'{response}'"
            )
            
        except Exception as ex:
            raise ex