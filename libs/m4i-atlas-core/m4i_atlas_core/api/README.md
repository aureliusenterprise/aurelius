# API

This README provides documentation for the M4I Atlas Core `api` module, which is designed for interacting with the Apache Atlas API and retrieving authentication tokens from Keycloak.

- [API](#api)
  - [Features](#features)
  - [How to use](#how-to-use)
    - [Submodules](#submodules)
    - [Atlas](#atlas)
      - [`create_entities`](#create_entities)
      - [`create_glossary`](#create_glossary)
      - [`create_glossary_category`](#create_glossary_category)
      - [`create_glossary_term`](#create_glossary_term)
      - [`create_type_defs`](#create_type_defs)
      - [`delete_entity_hard`](#delete_entity_hard)
      - [`delete_entity_soft`](#delete_entity_soft)
      - [`get_classification_def`](#get_classification_def)
      - [`get_entities_by_attribute`](#get_entities_by_attribute)
      - [`get_entities_by_type_name`](#get_entities_by_type_name)
      - [`get_entity_audit_events`](#get_entity_audit_events)
      - [`get_entity_by_guid`](#get_entity_by_guid)
      - [`get_glossary_by_guid`](#get_glossary_by_guid)
      - [`get_glossary_category_by_guid`](#get_glossary_category_by_guid)
      - [`get_glossary_term_by_guid`](#get_glossary_term_by_guid)
      - [`get_glossary`](#get_glossary)
      - [`get_lineage_by_guid`](#get_lineage_by_guid)
      - [`get_lineage_by_qualified_name`](#get_lineage_by_qualified_name)
      - [`get_type_def`](#get_type_def)
      - [`get_type_defs`](#get_type_defs)
      - [`update_type_defs`](#update_type_defs)
    - [Working with the cache](#working-with-the-cache)
  - [Auth](#auth)
    - [Usage](#usage)
    - [Configuration](#configuration)

## Features

The API module contains a set of functions that facilitate communication with the Apache Atlas API. These functions provide a convenient and efficient way to interact with the Aurelius Atlas platform. The main features of the API module include:

- Functions for creating, retrieving, updating, and deleting Atlas entities
- Functions for managing entity relationships and classifications
- Support for bulk operations, such as bulk entity creation and deletion
- Error handling and response parsing for API interactions

## How to use

To use any of the API functions, import them directly from the library:

```python
from m4i_atlas_core import create_entities, create_glossary, ...
```

### Submodules

The API module is divided into two submodules:

1. [`atlas`](#atlas): This submodule contains functions for interacting with the Apache Atlas API, enabling you to create, read, update, and delete entities and their related metadata.

2. [`auth`](#auth): This submodule is responsible for retrieving authentication tokens from Keycloak, which are required for accessing and utilizing the Apache Atlas API.

### Atlas

The `atlas` submodule provides a collection of functions to interact with the Apache Atlas API. These functions enable you to create, retrieve, update, and delete various entities, types, and glossaries in Apache Atlas.

The API functions make extensive use of the [data object model](../entities/atlas/README.md) included with this library, which corresponds to the data object model for the Apache Atlas API. You can find the official Apache Atlas API documentation at [this link](https://atlas.apache.org/api/v2/index.html).

The following sections include examples demonstrating how to use each API function.

#### `create_entities`

The `create_entities` function allows you to create or update multiple entities in Apache Atlas in bulk. It takes in a variable number of `Entity` objects and an optional dictionary of referred entities. It also accepts an optional access token for authentication purposes.

Here's an example of how to use the `create_entities` function:

```python
from m4i_atlas_core import Entity, create_entities

entity1 = Entity(...)
entity2 = Entity(...)

mutations = await create_entities(entity1, entity2)

print(mutations)
```

This example creates the two given entities in Apache Atlas. The `create_entities` function returns an `EntityMutationResponse` object containing the details of the entities created or updated.

#### `create_glossary`

The `create_glossary` function allows you to create a new glossary in Apache Atlas. It takes in a `Glossary` object and an optional access token for authentication purposes.

Here's an example of how to use the `create_glossary` function:

```python

from m4i_atlas_core import Glossary, create_glossary

glossary = Glossary(...)

created_glossary = await create_glossary(glossary)

print(created_glossary)
```

This example creates the given glossary in Apache Atlas. The `create_glossary` function returns a `Glossary` object containing the details of the created glossary.

#### `create_glossary_category`

The `create_glossary_category` function allows you to create a new glossary category in Apache Atlas. It takes in a `GlossaryCategory` object and an optional access token for authentication purposes.

Here's an example of how to use the `create_glossary_category` function:

```python
from m4i_atlas_core import GlossaryCategory, create_glossary_category

category = GlossaryCategory(...)

created_category = await create_glossary_category(category)

print(created_category)
```

This example creates the given glossary category in Apache Atlas. The `create_glossary_category` function returns a `GlossaryCategory` object containing the details of the created category.

#### `create_glossary_term`

The `create_glossary_term` function allows you to create a new glossary term in Apache Atlas. It takes in a `GlossaryTerm` object and an optional access token for authentication purposes.

Here's an example of how to use the `create_glossary_term` function:

```python
from m4i_atlas_core import GlossaryTerm, create_glossary_term

term = GlossaryTerm(...)

created_term = await create_glossary_term(term)

print(created_term)
```

This example creates the given glossary term in Apache Atlas. The `create_glossary_term` function returns a `GlossaryTerm` object containing the details of the created term.

#### `create_type_defs`

The `create_type_defs` function allows you to create multiple new type definitions in Apache Atlas in bulk. It takes in a `TypesDef` object and an optional access token for authentication purposes.

> **Note**: Only new definitions will be created, and any changes to the existing definitions will be discarded.

Here's an example of how to use the `create_type_defs` function:

```python
from m4i_atlas_core import TypesDef, EntityDef, create_type_defs

entity_def = EntityDef(...)

types_def = TypesDef(
    entity_defs=[entity_def]
)

created_type_defs = await create_type_defs(types_def)

print(created_type_defs)
```

This example creates the given entity definition in Apache Atlas. The `create_type_defs` function returns a `TypesDef` object containing lists of type definitions that were successfully created.

#### `delete_entity_hard`

The `delete_entity_hard` function allows you to permanently delete one or more entities from Apache Atlas by their `guid`. This operation removes the entities from the database completely.

It takes in a list of `guid` strings and an optional access token for authentication purposes.

> **Note**: This API requires elevated user permissions.

Here's an example of how to use the `delete_entity_hard` function:

```python
from m4i_atlas_core import delete_entity_hard

guids = ["1234-5678-90ab-cdef", "abcd-efgh-ijkl-mnop"]

mutations = await delete_entity_hard(guids)

print(mutations)
```

This example permanently deletes the entities with the given `guids` from Apache Atlas. The `delete_entity_hard` function returns an `EntityMutationResponse` object containing the details of the deleted entities.

#### `delete_entity_soft`

The `delete_entity_soft` function allows you to mark an entity as deleted in Apache Atlas without completely removing it from the database. The entity's status is set to `DELETED`. It takes in the `guid` of the entity and an optional access token for authentication purposes.

Here's an example of how to use the `delete_entity_soft` function:

```python
from m4i_atlas_core import delete_entity_soft

guid = "1234-5678-90ab-cdef"

mutations = await delete_entity_soft(guid)

print(mutations)
```

This example marks the entity with the given `guid` as deleted in Apache Atlas. The `delete_entity_soft` function returns an `EntityMutationResponse` object containing the details of the deleted entity.

#### `get_classification_def`

The `get_classification_def` function allows you to retrieve a classification definition from Apache Atlas based on its type name. It takes in the `type_name` of the classification and an optional access token for authentication purposes.

> **Note**: This function is _cached_, meaning that repeated calls with the same parameters will return the cached result rather than making additional requests to the server.

Here's an example of how to use the `get_classification_def` function:

```python
from m4i_atlas_core import get_classification_def

type_name = "example_classification"

classification_def = await get_classification_def(type_name)

print(classification_def)
```

This example retrieves the classification definition with the given `type_name` from Apache Atlas. The `get_classification_def` function returns a `ClassificationDef` object containing the details of the classification definition.

#### `get_entities_by_attribute`

The `get_entities_by_attribute` function allows you to retrieve entities from Apache Atlas based on a specified attribute search query. It takes in the `attribute_name`, `attribute_value`, and `type_name` as search parameters, and an optional access token for authentication purposes.

> **Note**: This function is _cached_, meaning that repeated calls with the same parameters will return the cached result rather than making additional requests to the server.

Keep in mind that this search only returns entity _headers_, which include the `guid` and `type_name` of the actual entity. You can use these headers to query the entities API for more information.

Here's an example of how to use the `get_entities_by_attribute` function:

```python
from m4i_atlas_core import get_entities_by_attribute

attribute_name = "example_attribute"
attribute_value = "example_value"
type_name = "example_type"

search_result = await get_entities_by_attribute(attribute_name, attribute_value, type_name)

print(search_result)
```

This example retrieves the entities with the given attribute and type from Apache Atlas. The `get_entities_by_attribute` function returns a `SearchResult` object containing the details of the entity headers that match the search query.

#### `get_entities_by_type_name`

The `get_entities_by_type_name` function allows you to search for all entities in Apache Atlas whose type matches the given `type_name`. It takes in the `type_name`, an optional `limit` and `offset` for pagination, and an optional access token for authentication purposes.

> **Note**: This function is _cached_, meaning that repeated calls with the same parameters will return the cached result rather than making additional requests to the server.

Keep in mind that this search only returns entity _headers_, which include the `guid` and `type_name` of the actual entity. You can use these headers to query the entities API for more information.

Here's an example of how to use the `get_entities_by_type_name` function:

```python

from m4i_atlas_core import get_entities_by_type_name

type_name = "example_type"

entities = await get_entities_by_type_name(type_name)

print(entities)
```

This example retrieves all entities with the given type from Apache Atlas. The `get_entities_by_type_name` function returns a list of `EntityHeader` objects containing the details of the entity headers that match the search query.

#### `get_entity_audit_events`

The `get_entity_audit_events` function allows you to fetch all audit events for an entity in Apache Atlas based on its `guid`. It takes in the `entity_guid` and an optional access token for authentication purposes.

> **Note**: This function is _cached_, meaning that repeated calls with the same parameters will return the cached result rather than making additional requests to the server.

Here's an example of how to use the `get_entity_audit_events` function:

```python
from m4i_atlas_core import get_entity_audit_events

entity_guid = "example_guid"

audit_events = await get_entity_audit_events(entity_guid)

print(audit_events)
```

This example fetches all audit events for the entity with the given `guid` from Apache Atlas. The `get_entity_audit_events` function returns a list of `EntityAuditEvent` objects containing the details of the audit events associated with the entity.

#### `get_entity_by_guid`

The `get_entity_by_guid` function allows you to fetch the complete definition of an entity in Apache Atlas based on its `guid`. It takes in the guid and an optional `entity_type`, which can be a string or an object of type `T`, where `T` is a subclass of `Entity`.

You can also provide optional parameters like `ignore_relationships` and `min_ext_info` to customize the results, as well as an optional access token for authentication purposes.

> **Note**: This function is _cached_, meaning that repeated calls with the same parameters will return the cached result rather than making additional requests to the server.

Here's an example of how to use the `get_entity_by_guid` function:

```python
from m4i_atlas_core import Entity, get_entity_by_guid

guid = "example_guid"

entity = await get_entity_by_guid(guid, Entity)

print(entity)
```

This example fetches the complete definition of the entity with the given `guid` from Apache Atlas. The `get_entity_by_guid` function returns an `Entity` object containing the details of the entity. If the `entity_type` parameter is provided, the function will return an instance of that type.

#### `get_glossary_by_guid`

The `get_glossary_by_guid` function allows you to fetch a glossary in Apache Atlas based on its `guid`. It takes in the `guid` of the glossary and an optional access token for authentication purposes.

> **Note**: This function is _cached_, meaning that repeated calls with the same parameters will return the cached result rather than making additional requests to the server.

Here's an example of how to use the `get_glossary_by_guid` function:

```python
from m4i_atlas_core import get_glossary_by_guid

guid = "example_glossary_guid"

glossary = await get_glossary_by_guid(guid)

print(glossary)
```

This example fetches the glossary with the given `guid` from Apache Atlas. The `get_glossary_by_guid` function returns a `Glossary` object containing the details of the glossary.

#### `get_glossary_category_by_guid`

The `get_glossary_category_by_guid` function allows you to fetch a glossary category in Apache Atlas based on its `guid`. It takes in the `guid` of the glossary category and an optional access token for authentication purposes.

> **Note**: This function is _cached_, meaning that repeated calls with the same parameters will return the cached result rather than making additional requests to the server.

Here's an example of how to use the `get_glossary_category_by_guid` function:

```python
from m4i_atlas_core import get_glossary_category_by_guid

guid = "example_glossary_category_guid"

glossary_category = await get_glossary_category_by_guid(guid)

print(glossary_category)
```

This example fetches the glossary category with the given `guid` from Apache Atlas. The `get_glossary_category_by_guid` function returns a `GlossaryCategory` object containing the details of the glossary category.

#### `get_glossary_term_by_guid`

The `get_glossary_term_by_guid` function allows you to fetch a glossary term in Apache Atlas based on its `guid`. It takes in the `guid` of the glossary term and an optional access token for authentication purposes.

> **Note**: This function is _cached_, meaning that repeated calls with the same parameters will return the cached result rather than making additional requests to the server.

Here's an example of how to use the `get_glossary_term_by_guid` function:

```python
from m4i_atlas_core import get_glossary_term_by_guid

guid = "example_glossary_term_guid"

glossary_term = await get_glossary_term_by_guid(guid)

print(glossary_term)
```

This example fetches the glossary term with the given `guid` from Apache Atlas. The `get_glossary_term_by_guid` function returns a `GlossaryTerm` object containing the details of the glossary term.

#### `get_glossary`

The `get_glossary` function allows you to fetch all glossaries in Apache Atlas with optional pagination and sorting. The function takes in an optional `limit`, `offset`, and sort `order`, as well as an optional access token for authentication purposes.

> **Note**: This function is _cached_, meaning that repeated calls with the same parameters will return the cached result rather than making additional requests to the server.

Here's an example of how to use the get_glossary function:

```python
from m4i_atlas_core import get_glossary

limit = 10
offset = 0
sort = 'ASC'

glossaries = await get_glossary(limit=limit, offset=offset, sort=sort)

for glossary in glossaries:
    print(glossary)
```

This example fetches glossaries from Apache Atlas using the specified pagination and sorting options. The `get_glossary` function returns a list of `Glossary` objects containing the details of the glossaries.

#### `get_lineage_by_guid`

The `get_lineage_by_guid` function allows you to fetch the lineage of an entity in Apache Atlas given its `guid`.

It takes in the `guid` of the entity, the maximum number of hops to traverse the lineage graph using the `depth` parameter (default is 3), the `direction` parameter to specify whether to retrieve input lineage, output lineage or both (default is both), and an optional access token for authentication purposes.

> **Note**: This function is _cached_, meaning that repeated calls with the same parameters will return the cached result rather than making additional requests to the server.

Here's an example of how to use the `get_lineage_by_guid` function:

```python
from m4i_atlas_core import LineageDirection, get_lineage_by_guid

guid = "12345"
depth = 3
direction = LineageDirection.BOTH

lineage_info = await get_lineage_by_guid(guid, depth=depth, direction=direction)

print(lineage_info)
```

This example fetches the lineage of the entity with the given `guid` from Apache Atlas. The `get_lineage_by_guid` function returns a `LineageInfo` object containing the details of the entity's lineage.

#### `get_lineage_by_qualified_name`

The `get_lineage_by_qualified_name` function allows you to fetch the lineage of an entity in Apache Atlas given its `qualified_name` and `type_name`.

It takes in the `qualified_name` and `type_name` of the entity, the maximum number of hops to traverse the lineage graph using the `depth` parameter (default is 3), the `direction` parameter to specify whether to retrieve input lineage, output lineage or both (default is both), and an optional access token for authentication purposes.

> **Note**: This function is _cached_, meaning that repeated calls with the same parameters will return the cached result rather than making additional requests to the server.

Here's an example of how to use the `get_lineage_by_qualified_name` function:

```python
from m4i_atlas_core import LineageDirection, get_lineage_by_qualified_name

qualified_name = "example.qualified.name"
type_name = "example_type_name"
depth = 3
direction = LineageDirection.BOTH

lineage_info = await get_lineage_by_qualified_name(qualified_name, type_name, depth=depth, direction=direction)

print(lineage_info)
```

This example fetches the lineage of the entity with the given `qualified_name` and `type_name` from Apache Atlas. The `get_lineage_by_qualified_name` function returns a `LineageInfo` object containing the details of the entity's lineage.

#### `get_type_def`

The `get_type_def` function allows you to retrieve an entity type definition from Apache Atlas based on its name. It takes in the `input_type` of the entity and an optional access token for authentication purposes.

> **Note**: This function is _cached_, meaning that repeated calls with the same parameters will return the cached result rather than making additional requests to the server.

Here's an example of how to use the `get_type_def` function:

```python

from m4i_atlas_core import get_type_def

input_type = "example_entity_type"

entity_def = await get_type_def(input_type)

print(entity_def)
```

This example retrieves the entity type definition with the given `input_type` from Apache Atlas. The `get_type_def` function returns an `EntityDef` object containing the details of the entity type definition.

#### `get_type_defs`

The `get_type_defs` function allows you to retrieve all type definitions in Apache Atlas. It takes an optional access token for authentication purposes.

> **Note**: This function is _cached_, meaning that repeated calls with the same parameters will return the cached result rather than making additional requests to the server.

Here's an example of how to use the `get_type_defs` function:

```python
from m4i_atlas_core import get_type_defs

type_defs = await get_type_defs()

print(type_defs)
```

This example retrieves all type definitions from Apache Atlas. The `get_type_defs` function returns a `TypesDef` object containing the details of the type definitions.

#### `update_type_defs`

The `update_type_defs` function allows you to bulk update all Apache Atlas type definitions. Existing definitions will be overwritten, but the function will not create any new type definitions.

It takes a types parameter, which is a `TypesDef` object containing the type definitions to be updated, and an optional access token for authentication purposes.

Here's an example of how to use the `update_type_defs` function:

```python
from m4i_atlas_core import EntityDef, TypesDef, update_type_defs

entity_def = EntityDef(
    category="ENTITY",
    name="example_entity",
    description="An example entity definition"
)

types = TypesDef(entityDefs=[entity_def])

updated_type_defs = await update_type_defs(types)

print(updated_type_defs)
```

This example updates an existing entity definition with the given types parameter in Apache Atlas. The `update_type_defs` function returns a `TypesDef` object containing the details of the type definitions that were successfully updated.

### Working with the cache

The library utilizes the [`aiocache`](https://aiocache.aio-libs.org/en/latest/) library to cache some API function results. Caching can help reduce server load and improve performance by reusing the results from previous API calls with the same parameters.

When you call a cached API function, the cache is automatically checked for the result. If the result is present in the cache, it is returned instead of making a new API call.

```python
from m4i_atlas_core import get_entity_by_guid

# Call the function once, making an API call
await get_entity_by_guid("12345")

# Call the function again, returning the result from the cache
await get_entity_by_guid("12345")

# Bypass the cache and make a direct API call
await get_entity_by_guid("12345", cache_read=False)
```

You can interact with the cache for any API function using the `cache` property. The following examples demonstrate how to access and manipulate the cache for the `get_entity_by_guid` function:

```python
from m4i_atlas_core import get_entity_by_guid

# Access the cache for the get_entity_by_guid function
cache = get_entity_by_guid.cache

# Delete an item from the cache
await cache.delete("12345")

# Clear the entire cache
await cache.clear()
```

These cache management options enable you to control and optimize the caching behavior of your application, tailoring it to your specific use case.

## Auth

The `auth` submodule provides functionality for retrieving authentication tokens from Keycloak, which are required for accessing the Apache Atlas API.

> **Note**: This module is specifically designed for use with Keycloak authentication. When Apache Atlas is configured with basic authentication, obtaining access tokens is not required. Instead, set a username and password in the `ConfigStore` for authentication.

### Usage

The `get_keycloak_token` function in the Auth submodule is responsible for retrieving an access token from a Keycloak instance.

To use the `get_keycloak_token` function, first import it:

```python
from m4i_atlas_core import get_keycloak_token
```

Next, call the function to retrieve an access token. You can provide your own Keycloak instance and credentials or rely on the pre-configured parameters from the `ConfigStore` as described in the [configuration](#configuration) section. If you need to use multi-factor authentication, provide the one-time access token (TOTP) as well.

```python
# Example: Using pre-configured parameters
access_token = get_keycloak_token()

# Example: Using custom Keycloak instance and credentials
access_token = get_keycloak_token(keycloak=my_keycloak_instance, credentials=("my_username", "my_password"))

# Example: Using multi-factor authentication (TOTP)
access_token = get_keycloak_token(totp="123456")
```

The `access_token` can then be used to authenticate requests to the Apache Atlas API.

> **Note**: Tokens obtained from Keycloak have a limited lifespan. Once a token expires, you will need to obtain a new access token to continue making authenticated requests.

### Configuration

The `get_keycloak_token` function relies on the following values from the `ConfigStore`:

| Key                             | Description                                                                                                                                                                                                                                                      | Required |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `keycloak.server.url`           | The url of the Keycloak server. In case of a local connection, this includes the hostname and the port. E.g. `http://localhost:8180/auth`. In case of an external connection, provide a fully qualified domain name. E.g. `https://www.models4insight.com/auth`. | `True`   |
| `keycloak.client.id`            | The name of the Keycloak client.                                                                                                                                                                                                                                 | `True`   |
| `keycloak.realm.name`           | The name of the Keycloak realm.                                                                                                                                                                                                                                  | `True`   |
| `keycloak.client.secret.key`    | The public RS256 key associated with the Keycloak realm.                                                                                                                                                                                                         | `True`   |
| `keycloak.credentials.username` | The username of the Keycloak user.                                                                                                                                                                                                                               | `False`  |
| `keycloak.credentials.password` | The password of the Keycloak user.                                                                                                                                                                                                                               | `False`  |

[Please find more detailed documentation about `ConfigStore` here.](../config/README.md)
