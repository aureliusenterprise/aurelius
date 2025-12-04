.. include:: substitutions.rst

|Equipment assigned to facility|
================================

.. author Qu

Description
-----------




Non-compliance conditions
-------------------------

A relationship is non-compliant if

- **Equipment** and **facilities** are related via a different relationship than **assignment** relationship


Non-compliance report
---------------------

The non-compliance report contains non-compliant relationships described by the following columns:

==================== =========================================================================================
Equipment assigned to facility
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

Replace the non-compliant relationship by an **assignment** relationship.


Related consistency metrics
---------------------------

- Physical Metrics


Related guidelines
------------------

None