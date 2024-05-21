# Data Object Model

This section provides an overview of how to use the data object model provided in the library. The data objects are designed to represent various types of entities, attributes, classifications, and other components in Aurelius Atlas. They are used extensively when interacting with the Atlas API.

- [Data Object Model](#data-object-model)
  - [Features](#features)
  - [How to use](#how-to-use)
    - [Submodules](#submodules)
    - [Creating Entities and Relationships](#creating-entities-and-relationships)
      - [Creating an Entity](#creating-an-entity)
      - [Creating a Relationship](#creating-a-relationship)
    - [Serialization and deserialization](#serialization-and-deserialization)
      - [From JSON to Instance](#from-json-to-instance)
        - [Unmapped attributes](#unmapped-attributes)
      - [From Instance to JSON](#from-instance-to-json)
    - [Marshmallow Schema](#marshmallow-schema)
      - [Data Validation](#data-validation)
      - [Bulk Serialization and Deserialization](#bulk-serialization-and-deserialization)

## Features

The entities module provides a collection of data objects designed to represent different types of entities, attributes, classifications, and other components in Aurelius Atlas. The main features of the entities module include:

- Data objects related to the Apache Atlas API
- Data objects related to the Aurelius Atlas metamodel
- Convenience methods for converting data objects to and from JSON format
- Marshmallow schemas for data validation, serialization, and deserialization

## How to use

To use the data objects from the library in your code, you can easily import them. For example, if you want to work with the `Entity` data object, you can import it as follows:

```python
from m4i_atlas_core import Entity
```

Once you have imported the desired data object, you can create instances, access their properties, and manipulate them as needed.

### Submodules

The `entities` module is organized into two main submodules:

- `core`: This submodule includes data objects that correspond to the Apache Atlas API. These objects are used for representing entities, classifications, relationships, and other components as defined in Apache Atlas.
- `data_dictionary`: This submodule contains data objects that are specific to the Aurelius Atlas metamodel. These objects extend or customize the core data objects to better suit the requirements of the Aurelius Atlas platform.

### Creating Entities and Relationships

The data objects from the `entities` module enable manipulation of entities and relationships in your data governance model. This module provides data objects for various types of entities in Aurelius Atlas.

This section includes examples demonstrating how to create new entities and relationships.

> **Note**: All data objects representing entities inherit from the core `Entity` type and can be used with API functions that expect an `Entity` object as input.

#### Creating an Entity

Let's create a new `BusinessDataDomain` entity in Aurelius Atlas.

```python
from m4i_atlas_core import BusinessDataDomain, BusinessDataDomainAttributes

# Each entity type has a corresponding attributes object.
# The name and qualified_name attributes are always required.
data_domain_attributes = BusinessDataDomainAttributes(
    name="Example Data Domain",
    qualified_name="example.data.domain"
)

# Now, create the main data domain object and assign the attributes object to it.
data_domain = BusinessDataDomain(
    attributes=data_domain_attributes
)
```

This example demonstrates the creation of a basic `BusinessDataDomain` entity, which can be used with the `create_entities` API function to save the entity to Aurelius Atlas.

> **Note**: By default, new entities are assigned a placeholder `guid`. Placeholder `guids` are easily recognizable as they begin with a `-`, for example, `-1234`. After the entity is saved to Aurelius Atlas, it will be given a permanent `guid`.

#### Creating a Relationship

Next, let's create a relationship between our `BusinessDataDomain` and another entity in Aurelius Atlas. For example, let's assign a domain owner responsible for all data in this particular domain. We will represent the data owner with a new `AtlasPerson` entity and create a relationship to the `BusinessDataDomain`.

```python
from m4i_atlas_core import AtlasPerson, AtlasPersonAttributes

# Let's assign a domain lead for our BusinessDataDomain
# We start by defining a new AtlasPerson
person_attributes = AtlasPersonAttributes(
    qualified_name="example.data.owner",
    name="John Doe",
    email="john.doe@example.com"
)

# Next, create the main person object and assign the attributes object to it.
person = AtlasPerson(
    attributes=person_attributes
)
```

Now that we have defined a new `AtlasPerson`, let's associate it with the `BusinessDataDomain` we created previously. We need to define a reference using an `ObjectId`. References can be made either based on the `guid` of an entity or a unique attribute like `qualified_name`. Since we are defining a new `AtlasPerson` and do not know its `guid` yet, let's create a reference by `qualified_name`:

```python
from m4i_atlas_core import M4IAttributes, ObjectId

# Let's create a reference to our AtlasPerson that we can assign to the BusinessDataDomain.
domain_lead_ref = ObjectId(
    type_name=person.type_name,
    unique_attributes=M4IAttributes(
        qualified_name=person_attributes.qualified_name
    )
)

# Finally, we include the reference as part of the domain lead attribute.
data_domain_attributes.domain_lead = [domain_lead_ref]
```

This code snippet creates an `ObjectId` reference using the `qualified_name` of the `AtlasPerson` and assigns it to the `domain_lead` attribute of the `BusinessDataDomain`. This association establishes the relationship between the two entities.

With this relationship defined, you can use the `create_entities` API function to save the entities and their relationships to Aurelius Atlas, effectively connecting the `BusinessDataDomain` to its corresponding `domain_lead` in the data governance model.

### Serialization and deserialization

Each data object is a [`dataclass`](https://docs.python.org/3/library/dataclasses.html) and is designed to be easily serialized and deserialized using the [`dataclasses_json`](https://lidatong.github.io/dataclasses-json/) library. This allows for convenient conversion between JSON and the corresponding data object instances.

The `dataclasses_json` library provides additional features such as `camelCase` to `snake_case` letter conversion and other customizations.

Below are some examples of how to use a data object, such as `BusinessDataDomain`, to convert between its instance and JSON representation.

#### From JSON to Instance

You can convert JSON data to an `Entity` instance using the `from_json()` method.
Suppose you have the following JSON representation of a data domain:

```json
{
  "attributes": {
    "key": "value",
    "name": "example",
    "qualifiedName": "data-domain--example"
  },
  "guid": "12345",
  "typeName": "m4i_data_domain"
}
```

The example below demonstrates how to create a `BusinessDataDomain` instance from the given JSON data:

```python
from m4i_atlas_core import BusinessDataDomain

json_data = '''JSON string here'''
domain_instance = BusinessDataDomain.from_json(json_data)
```

##### Unmapped attributes

In the given example, the `key` attribute is not explicitly defined as part of the schema for `BusinessDataDomain`. In such cases, the attributes field of the resulting instance will include an `unmapped_attributes` field. This field offers flexibility when working with entities containing additional or custom attributes not specified in the predefined data model. The `unmapped_attributes` field acts as a catch-all for these attributes, ensuring they are preserved during the conversion process between JSON and the `Entity` instance.

To access an unmapped attribute, you can use the following code:

```python
value = domain_instance.attributes.unmapped_attributes["key"]
```

When converting any `Entity` instance back to JSON, the unmapped attributes will be included as part of the `attributes` field once again.

#### From Instance to JSON

To convert an `Entity` instance back to its JSON representation, use the `to_json()` method. 
The example below shows how to convert the `BusinessDataDomain` instance we created previously back to its JSON representation:

```python
json_data = domain_instance.to_json()
```

This will return a JSON string that represents the data domain instance, including any unmapped attributes.

### Marshmallow Schema

Each data object in the library is equipped with a built-in Marshmallow schema. These schemas are valuable tools for validating, serializing, and deserializing complex data structures. By utilizing Marshmallow schemas, you can ensure that the data being passed to or returned from the API adheres to the correct structure and data types.

To access the Marshmallow schema for any data object, use the `schema()` method:

```python
from m4i_atlas core import Entity

schema = Entity.schema()
```

#### Data Validation

Marshmallow schemas associated with the data objects in this library can be employed to perform data validation. The following example demonstrates how to use a Marshmallow schema to validate JSON input data:

```python
from m4i_atlas_core import Entity

# Load the schema for the Entity data object
entity_schema = Entity.schema()

# Validate input data
input_data = {
    "guid": "123",
    "created_by": "user",
    "custom_attributes": {"key": "value"},
}

errors = entity_schema.validate(input_data)

if errors:
    print(f"Validation errors: {errors}")
else:
    print("Data is valid")
```

In this example, the `Entity` data object from the library is used to validate the `input_data` JSON using its associated Marshmallow schema. If the data is valid, the `validate` method will not return any errors, and the "Data is valid" message will be displayed. If the data is invalid, a dictionary containing the validation errors will be returned.

This approach can be applied to other data objects in the library for validating JSON input data using their respective Marshmallow schemas. To read more about data validation with Marshmallow, refer to [the official documentation](https://marshmallow.readthedocs.io/en/stable/quickstart.html#validation).

#### Bulk Serialization and Deserialization

Marshmallow schemas can be utilized for bulk serialization and deserialization of complex data structures. This is particularly useful when working with lists of data objects.

To serialize a list of data objects into a JSON format, you can use the dump method with the `many=True` option:

```python
from m4i_atlas_core import Entity

# Sample list of Entity data objects
entities = [
    Entity(guid="1", created_by="user1", custom_attributes={"key1": "value1"}),
    Entity(guid="2", created_by="user2", custom_attributes={"key2": "value2"}),
]

# Load the schema for the Entity data object
entity_schema = Entity.schema()

# Serialize the list of entities
serialized_data = entity_schema.dump(entities, many=True)

print("Serialized data:", serialized_data)
```

To deserialize a JSON list of data objects, you can use the load method with the `many=True` option:

```python
from m4i_atlas_core import Entity

# Sample JSON list of entity data
json_data = [
    {"guid": "1", "created_by": "user1", "custom_attributes": {"key1": "value1"}},
    {"guid": "2", "created_by": "user2", "custom_attributes": {"key2": "value2"}},
]

# Load the schema for the Entity data object
entity_schema = Entity.schema()

# Deserialize the JSON list of entities
deserialized_data = entity_schema.load(json_data, many=True)

print("Deserialized data:", deserialized_data)
```

In both examples, the `many=True` option is specified to indicate that the data being processed is a list. You can apply the same approach with other data objects in the library to perform bulk serialization and deserialization using their corresponding Marshmallow schemas.
