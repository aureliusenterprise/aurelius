from ...m4i_generic_entity_serializers import *

m4i_confluentCloud_entity_model = api.model('model_m4i_confluentCloud_entity', {
    "name": fields.String(required=True, description="The Name of the Confluent Cloud")
})
