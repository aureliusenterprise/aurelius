import json
import logging
import re
from typing import Dict, List, Tuple, Callable, Union

from m4i_atlas_core import (
    AtlasPerson,
    BusinessDataDomain,
    BusinessDataEntity,
    BusinessDataAttribute,
    BusinessField,
    BusinessDataset,
    BusinessCollection,
    BusinessSystem,
    BusinessSource,
    BusinessDataQuality,
    BusinessGovDataQuality,
    GenericProcess,
)
from m4i_flink_tasks.model.gov_data_quality_document import GovDataQualityDocument
from marshmallow import ValidationError
from pyflink.datastream import DataStream
from pyflink.datastream.functions import MapFunction

from m4i_governance_data_quality import get_rules_for_type, calculate_gov_quality
from keycloak import KeycloakOpenID

# A type alias for a factory function that produces instances of KeycloakOpenID.
KeycloakFactory = Callable[[], KeycloakOpenID]

ATLAS_ENTITY_TYPES = {
    "m4i_source": BusinessSource,
    "m4i_person": AtlasPerson,
    "m4i_data_domain": BusinessDataDomain,
    "m4i_data_entity": BusinessDataEntity,
    "m4i_data_attribute": BusinessDataAttribute,
    "m4i_field": BusinessField,
    "m4i_dataset": BusinessDataset,
    "m4i_collection": BusinessCollection,
    "m4i_system": BusinessSystem,
    "m4i_data_quality": BusinessDataQuality,
    "m4i_gov_data_quality": BusinessGovDataQuality,
    "m4i_generic_process": GenericProcess,
}


class GetRulesFunction(MapFunction):
    """
    A PyFlink map function that creates GovDataQualityDocuments with from an entity.

    If the entity is missing or there's an HTTP error during the enrichment, it outputs an
    error message to a side output. Utilizes a Keycloak instance to manage authentication tokens.
    """

    def map(
        self, value: str
    ) -> Union[List[Tuple[str, Union[GovDataQualityDocument, None]]], Exception]:
        """
        Processes an incoming JSON message and maps it to a list of GovDataQualityDocument objects
        based on associated rules.

        Parameters
        ----------
        value : str
            The input JSON message containing an entity and its details.

        Returns
        -------
        List[Tuple[str, Union[GovDataQualityDocument, None]]]
            A list of tuples containing IDs and their corresponding GovDataQualityDocument objects or None.
        Exception
            If an error occurs during processing.
        """

        logging.debug("Governance Data Quality rules: %s", value)

        try:
            # Convert the JSON string into a Python dictionary.
            json_object = json.loads(value)
            # Get the type name of the object to determine its class.
            object_type: str = json_object["value"]["typeName"]
            # Find the corresponding class from the ATLAS_ENTITY_TYPES dictionary.
            atlas_type = ATLAS_ENTITY_TYPES[object_type]
            # Deserialize the JSON data into an object of the determined class.
            entity = atlas_type.from_json(json.dumps(json_object["value"]))
        except ValidationError as e:
            logging.exception("Error deserializing message")
            return e
        except KeyError:
            return ValueError(f"Unexpected type. TypeName={object_type}")

        logging.info("Successfully deserialized message: %s", entity)

        if entity is None:
            logging.debug("No entity found in message: %s", entity)
            return ValueError(f"No entity found in message. Value={value}")

        # Retrieve applicable rules for the entity type
        try:
            rules = get_rules_for_type(object_type)
        except Exception:
            return ValueError("Creating rules, skipping type %s.", object_type)

        # 3. Enrich rules based on the entity
        updated_rules: Dict[str, Union[GovDataQualityDocument, None]] = {}

        # Create or update rules if the entity has a create_time
        if entity.create_time:
            gov_results = calculate_gov_quality(entity, rules=rules).values.flatten().tolist()

            if len(rules) != len(rules):
                raise ValueError("Mismatch between rules and results")

            for rule, compliant in zip(rules, gov_results):
                id = f"{entity.guid}--{rule.guid}"
                attribute_match = re.search(r"'(.*?)'", rule.expression)

                if not attribute_match:
                    raise ValueError("Invalid or missing attribute in rule expression")

                used_attribute = attribute_match.group(1)

                updated_rules[id] = GovDataQualityDocument(
                    id=id,
                    guid=rule.guid,
                    name=rule.rule_title,
                    qualifiedname=id,
                    qualityqualifiedname=rule.qualified_name,
                    dataqualityruletypename=entity.type_name,
                    dataqualitytype=rule.type,
                    dataqualityruledescription=rule.rule_description,
                    dataqualityruledimension=rule.quality_dimension,
                    result_id="0",
                    business_rule_id="1",
                    compliant=compliant,
                    noncompliant_message=rule.noncompliant_message,
                    entity_guid=entity.guid,
                    expression=rule.expression,
                    usedattributes=[used_attribute],
                )
        else:
            # Delete rules for entities without creation time
            for rule in rules:
                id = f"{entity.guid}--{rule.guid}"
                updated_rules[id] = None

        logging.info("Processed rules: %s", updated_rules)

        return list(updated_rules.items())

class GetRules:
    """
    A class to handle the data stream and process it using the GetRulesFunction.

    This class initializes the main data stream, processes it, and handles errors by
    directing them to side outputs.

    Attributes
    ----------
    data_stream : DataStream
        The main data stream to be processed.
    main : DataStream
        The main data stream after processing with GetRulesFunction.
    """

    def __init__(
        self,
        data_stream: DataStream,
    ) -> None:
        """
        Initialize the GetRules class with a given data stream.

        Parameters
        ----------
        data_stream : DataStream
            The input data stream to be processed.
        atlas_url : str
            The URL of the Apache Atlas API.
        keycloak_factory : KeycloakFactory
            A factory function to produce instances of KeycloakOpenID.
        """
        self.data_stream = data_stream

        self.rules = self.data_stream.map(
            GetRulesFunction(),
        ).name("enriched_rules")

        self.filtered_rules = self.rules.filter(
            lambda messages: isinstance(messages, list)
        ).name("filtered_rules")

        self.main = self.filtered_rules.flat_map(
            lambda messages: (
                message for message in messages
            ),
        ).name("flattened_messages")
