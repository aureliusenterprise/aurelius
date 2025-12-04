.. include:: substitutions.rst

|Misconnected junctions|
=========================

.. author Qu

Description
-----------




Non-compliance conditions
-------------------------

A **junction** element is non-compliant if

- it is connected to more than one **relationship type**
- it is connected to zero **incoming** relationships
- it is connected to zero **outgoing** relationships


Non-compliance report
---------------------

The non-compliance report for relationship types contains non-compliant junctions described by the following columns:

============================ =========================================================================================
Junctions with multiple types
----------------------------------------------------------------------------------------------------------------------
Column                       Description
============================ =========================================================================================
Junction ID                  junction UUID (Universally Unique Identifier) causing the non-compliance

Junction type                junction type causing the non-compliance

Junction relationship types  types of relationships connected to the reported junction
============================ =========================================================================================

The non-compliance report for relationship counts contains non-compliant junctions described by the following columns:

=============================== =========================================================================================
Junctions missing relations
-------------------------------------------------------------------------------------------------------------------------
Column                           Description
=============================== =========================================================================================
Junction ID                      junction UUID (Universally Unique Identifier) causing the non-compliance

Junction type                    junction type causing the non-compliance

Count of incoming relationships  number of incoming relationships connected to the reported junction

Count of outgoing relationships  number of outgoing relationships connected to the reported junction
=============================== =========================================================================================

Resolution
----------
- Make sure each **junction** has relationships connected to it of at most one **relationship type**.
- Make sure each **junction** has at least one **incoming** and at least one **outgoing** relationship.


Related consistency metrics
---------------------------

- Structural Metrics


Related guidelines
------------------

- None

