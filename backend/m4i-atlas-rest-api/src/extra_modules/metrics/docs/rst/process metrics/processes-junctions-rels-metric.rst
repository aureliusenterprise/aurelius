.. include:: substitutions.rst

|Process sequence & abstraction|
===============================

.. author Qu

Description
-----------




Non-compliance conditions
-------------------------

A relationship is non-compliant if

- **Business processes** are related via a different relationship than **aggregation,composition, trigger** or **specialization** relationship
- **Application processes** are related via a different relationship than **aggregation, composition, trigger** or **specialization** relationship
- **Technology processes** are related via a different relationship than **aggregation, composition, trigger** or **specialization** relationship

If **processes** are related via **trigger**, there can be **and-junctions/or-junctions** in-between to create a **path** of sequential relationships 

- A relationship is non-compliant if it is part of a **path** and related via a different relationship than **trigger** relationship


Non-compliance report
---------------------

The non-compliance report contains non-compliant relationships described by the following columns:

==================== =========================================================================================
Process sequence & abstraction
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

==================== ===================================================================================================
Process sequence & abstraction with junctions
------------------------------------------------------------------------------------------------------------------------
Column               Description
==================== ===================================================================================================
Relationship ID      relationship UUID (Universally Unique Identifier) causing the non-compliance

Relationship type    relationship type causing the non-compliance

Start name           name of the process start of the path the reported relationship is a part of

Start type           ArchiMate type of the process start of the path the reported relationship is a part of

Source type          ArchiMate type of the source concept of the reported relationship

Target type          ArchiMate type of the target concept of the reported relationship

End name             name of the process end of the path the reported relationship is a part of

End type             ArchiMate type of the process end of the path the reported relationship is a part of
==================== ===================================================================================================

Resolution
----------

Replace the non-compliant relationship by an **aggregation, composition, trigger** or **specialization** relationship.


Related consistency metrics
---------------------------

- Process Metrics


Related guidelines
------------------
- Processes are constructed using trigger relations 
- Process steps in the sub process structure are connected via specific relationships to the main process step
- Organize processes – potentially along multiple dimensions
- Use processes for more detailed and executable processes (composition/aggregation relationship)

