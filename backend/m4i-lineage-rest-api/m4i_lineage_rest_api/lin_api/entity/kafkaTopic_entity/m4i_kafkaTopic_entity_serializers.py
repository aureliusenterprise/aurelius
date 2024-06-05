from flask_restx import fields

from ...restplus import api


class StringOrObjectOrArrayElement(fields.Raw):
    __schema_type__ = ['string', 'object', 'array']


class StringOrObjectElement(fields.Raw):
    __schema_type__ = ['string', 'object']


class StringOrObjectElement(fields.Nested):
    # https://stackoverflow.com/questions/49793006/flask-restplus-how-to-model-string-or-object
    __schema_type__ = ['string', 'object']

    # def output(self, key, obj):
    #     if isinstance(obj, str):
    #         if key == 'name':
    #             return obj
    #         else:
    #             return 'default_value'
    #     return super().output(key, obj)

    def schema(self):
        schema_dict = super().schema()
        schema_dict.pop('type')
        nested_ref = schema_dict['allOf'][0].pop('$ref')
        schema_dict['oneOf'] = [
            {
                'type': 'string'
            },
            {
                '$ref': nested_ref
            }
        ]
        return schema_dict


class NullableStringList(fields.String):
    __schema_type__ = ['string', 'null', 'array']
    # __schema_example__ = 'nullable string'


m4i_kafkaTopic_entity_field = api.model('field_m4i_kafkaTopic_entity', {
    'name': fields.String(),
    'doc': NullableStringList(required=True),
    'type': StringOrObjectOrArrayElement(required=True)
})

m4i_kafkaTopic_entity_fields = api.model('fields_m4i_kafkaTopic_entity', {
    'fields': fields.List(fields.Nested(m4i_kafkaTopic_entity_field), required=True),
    'name': fields.String(required=True),
    'doc': NullableStringList(required=True),
    'type': StringOrObjectOrArrayElement(required=True)

})

m4i_kafkaTopic_entity_model = api.model('model_m4i_kafkaTopic_entity', {
    'name': fields.String(required=True, description='The name of hte kafka topic'),
    'environment': fields.String(required=True,
                                 description='The name of the confluent environment the kafka topic is on'),
    'cluster': fields.String(required=True, description='The name of kafka cluster the kafka topic is on'),
    'partitions': fields.Integer(required=True, description='The partitions configured for the kafka topic'),
    'replicas': fields.Integer(required=True, description='The replicas configured for the kafka topic'),
    'key_schema': fields.String(required=True, description='The key schema configured for the kafka topic'),  # avo
    'value_schema': StringOrObjectElement(m4i_kafkaTopic_entity_fields, required=True,
                                          description='The value schema configured for the kafka topic')
})
