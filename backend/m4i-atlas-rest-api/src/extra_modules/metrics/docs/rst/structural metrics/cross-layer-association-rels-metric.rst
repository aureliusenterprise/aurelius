.. include:: substitutions.rst

|Use of association relations|
=========================

.. author Qu

Description
-----------




Non-compliance conditions
-------------------------

A **association** relationship is non-compliant if

- **both** the **source** concept and the **target** concept of the relationship is in the **business layer**, **application layer**, **technology layer**, **physical layer** or **junctions**

- The 13 concepts in the **business layer** are **business actor, business role, business collaboration, business interface, business process, business function, business interaction, business event, business service, business object, contract, representation** and **product**
- The 9 concepts in the **application layer** are **application component, application collaboration, application interface, application function, application interaction, application process, application event, application service** and **data object**
- The 13 concepts in the **technology layer** are **node, device, system software, technology collaboration, technology interface, path, communication network, technology function, technology process, technology interaction, technology event, technology service** and **artifact**
- The 4 concepts in the **physical layer** are **equipment, facility, distribution network** and **material**
- The 2 concepts in **junctions** are **and-junctions** and **or-junctions**



Non-compliance report
---------------------

The non-compliance report contains non-compliant relationships described by the following columns:

==================== =========================================================================================
Use of association relations
--------------------------------------------------------------------------------------------------------------
Column               Description
==================== =========================================================================================
Relationship ID      relationship UUID (Universally Unique Identifier) causing the non-compliance

Relationship type    relationship type causing the non-compliance

Source name          name of the source concept of the reported relationship

Source type          ArchiMate type of the source concept of the reported relationship

Target name          name of the target concept of the reported relationship

Target type          ArchiMate type of the target concept of the reported relationship
==================== =========================================================================================

Resolution
----------

Limit the use of **association** relationships in your models.


Related consistency metrics
---------------------------

- Structural Metrics


Related guidelines
------------------

- None

