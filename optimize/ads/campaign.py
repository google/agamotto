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
import sys

from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads import oauth2
from google.api_core import protobuf_helpers
from utils.logger import logger

_BUDGET_TEMPORARY_ID = -1

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
                campaign_id = row['CampaignId']
                store_id = row['StoreId'].split(',')
                sales_up_threshold = int(row['SalesUpThreshold']) + 100
                sales_down_threshold = 100 - int(row['SalesDownThreshold'])
                visits_up_threshold = int(row['VisitsUpThreshold']) + 100
                visits_down_threshold = 100 - int(row['VisitsDownThreshold'])
                for id in store_id:
                    if int(id) in deltas:
                        (delta_sales, delta_count) = deltas[int(id)]
                        # 120, 116 - 80, 116
                        if delta_sales < sales_down_threshold:
                            logger(self.__class__.__name__).info(f"Updating campaign for StoreId: {id}")
                            self.update_campaign_status(customer_id,campaign_id, "enable")
                            # campaign.update_campaign_status(customer_id,campaign_id, "enable")
                        if delta_count < visits_down_threshold:
                            logger(self.__class__.__name__).info(f"Updating campaign for StoreId: {id}")
                            self.update_campaign_status(customer_id,campaign_id, "enable")
                            # campaign.update_campaign_status(customer_id,campaign_id, "enable")
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
    
    def create_campaign_budget_operation(client, customer_id):
        """Creates a MutateOperation that creates a new CampaignBudget.
        A temporary ID will be assigned to this campaign budget so that it can be
        referenced by other objects being created in the same Mutate request.
        Args:
            client: an initialized GoogleAdsClient instance.
            customer_id: a client customer ID.
        Returns:
            a MutateOperation that creates a CampaignBudget.
        """
        mutate_operation = client.get_type("MutateOperation")
        campaign_budget_operation = mutate_operation.campaign_budget_operation
        campaign_budget = campaign_budget_operation.create
        campaign_budget.name = f"Agamotto - Budget"
        # The budget period already defaults to DAILY.
        campaign_budget.amount_micros = 500000
        campaign_budget.delivery_method = (
            client.enums.BudgetDeliveryMethodEnum.STANDARD
        )
        # A Performance Max campaign cannot use a shared campaign budget.
        campaign_budget.explicitly_shared = False

        # Set a temporary ID in the budget's resource name so it can be referenced
        # by the campaign in later steps.
        campaign_budget.resource_name = client.get_service(
            "CampaignBudgetService"
        ).campaign_budget_path(customer_id, _BUDGET_TEMPORARY_ID)

        return mutate_operation

    def create_performance_max_campaign_operation(client,customer_id):
        """Creates a MutateOperation that creates a new Performance Max campaign.
        A temporary ID will be assigned to this campaign so that it can
        be referenced by other objects being created in the same Mutate request.
        Args:
            client: an initialized GoogleAdsClient instance.
            customer_id: a client customer ID.
        Returns:
            a MutateOperation that creates a campaign.
        """
        mutate_operation = client.get_type("MutateOperation")
        campaign = mutate_operation.campaign_operation.update
        campaign.name = f"Agamoto 29 Aug"

        # Assign the resource name with a temporary ID.
        campaign_service = client.get_service("CampaignService")
        campaign.resource_name = campaign_service.campaign_path(
            customer_id, _PERFORMANCE_MAX_CAMPAIGN_TEMPORARY_ID
        )
        # Set the budget using the given budget resource name.
        campaign.campaign_budget = campaign_service.campaign_budget_path(
            customer_id, _BUDGET_TEMPORARY_ID
        )

        # Optional fields
        campaign.start_date = (datetime.now() + timedelta(1)).strftime("%Y%m%d")
        campaign.end_date = (datetime.now() + timedelta(365)).strftime("%Y%m%d")

        return mutate_operation

    def old_budget_creation(self, customer_id):
        # Create a budget, which can be shared by multiple campaigns.
        campaign_budget_operation = self._googleads_client.get_type("CampaignBudgetOperation")
        campaign_budget = campaign_budget_operation.create
        campaign_budget.name = f"Agamotto Budget"
        campaign_budget.amount_micros = 500000
        campaign_budget.explicitly_shared = False
        try:
            campaign_budget_response = (
                self._googleads_client.get_service("CampaignBudgetService").mutate_campaign_budgets(
                    customer_id=customer_id, operations=[campaign_budget_operation]
                )
            )
            return campaign_budget_response
        except Exception as ex:
            raise ex
        
    def old_campaign_update(self, customer_id, campaign_id):
        campaign_service = self._googleads_client.get_service("CampaignService")
        campaign_operation = self._googleads_client.get_type("CampaignOperation")
        campaign = campaign_operation.update
        campaign.resource_name = campaign_service.campaign_path(
            customer_id, campaign_id
        )
        campaign_budget_response = self.old_budget_creation(customer_id=customer_id)
        print(campaign_budget_response.results[0].resource_name)
        campaign.campaign_budget = campaign_budget_response.results[0].resource_name
    
        try:
            self._googleads_client.copy_from(
                campaign_operation.update_mask,
                protobuf_helpers.field_mask(None, campaign._pb),
            )
            campaign_response = campaign_service.mutate_campaigns(
                customer_id=customer_id, operations=[campaign_operation]
            )
            print(f"Updated campaign {campaign_response.results[0].resource_name}.")
        except Exception as ex:
            raise ex