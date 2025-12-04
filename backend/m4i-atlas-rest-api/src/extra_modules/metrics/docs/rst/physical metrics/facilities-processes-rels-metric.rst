.. include:: substitutions.rst

|Material flow|
===============================

.. author Qu

Description
-----------




Non-compliance conditions
-------------------------

A relationship is non-compliant if

- **Business processes** and **facilities** are related via a **trigger** relationship
- **Application processes** and **facilities** are related via a **trigger** relationship
- **Technology processes** and **facilities** are related via a **trigger** relationship

If **processes** and **facilities** are related, there can be **and-junctions/or-junctions** in-between to create a **path** of sequential relationships 

- A relationship is non-compliant if it is part of a **path** and related via a **trigger** relationship


Non-compliance report
---------------------

The non-compliance report contains non-compliant relationships described by the following columns:

==================== =========================================================================================
Material flow
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

If the relationships are part of a **path** connected to junctions, non-compliant relationships are described by the following columns:

==================== =============================================================================================================
Material flow with junctions
----------------------------------------------------------------------------------------------------------------------------------
Column               Description
==================== =============================================================================================================
Relationship ID      relationship UUID (Universally Unique Identifier) causing the non-compliance

Relationship type    relationship type causing the non-compliance

Start name           name of the process start/facility start of the path the reported relationship is a part of

Start type           ArchiMate type of the process start/facility start of the path the reported relationship is a part of

Source type          ArchiMate type of the source concept of the reported relationship

Target type          ArchiMate type of the target concept of the reported relationship

End name             name of the process end/facility end of the path the reported relationship is a part of

End type             ArchiMate type of the process end/facility end of the path the reported relationship is a part of
==================== =============================================================================================================

Resolution
----------

Replace the non-compliant relationship by a relationship that is not **trigger**, for example a **flow** relationship


Related consistency metrics
---------------------------

- Physical Metrics


Related guidelines
------------------
- In push processes material flow triggers processes by having material at some specific location


