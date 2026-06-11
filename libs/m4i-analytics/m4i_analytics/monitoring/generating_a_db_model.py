from pandas import DataFrame
from sqlalchemy import MetaData, create_engine

from m4i_analytics.graphs.languages.archimate.ArchimateUtils import ArchimateUtils
from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import ElementType, RelationshipType
from m4i_analytics.graphs.languages.archimate.model.ArchimateModel import ArchimateModel, ViewAttribute
from m4i_analytics.graphs.visualisations.GraphPlotter import Layout as LayoutEnum
from m4i_analytics.model_extractor.model.Extractor import ExtractionResult, Extractor


class DBExtractor(Extractor):
    script_name = "db model generator"
    db_url = None

    def __init__(
        self,
        db_url,
        branch_name="db",
        log_file_path=None,
        log_file_format=(
            "%(asctime)s - %(name)s -%(relativeCreated)6d %(threadName)s - %(levelname)s - %(message)s"
        ),
    ):
        super().__init__(branch_name, log_file_path, log_file_format)
        self.db_url = db_url

    # END __init__

    def getConnection(self, db):
        engine = create_engine(db, echo=False)
        return engine

    # END getConnection

    def formatTableName(self, db_name, schema_name, table_name):
        return "{}.{}{}".format(db_name, (f"{schema_name}.") * bool(schema_name), table_name)

    # END formatTableName

    def getDBName(self, url):
        return url.split("/")[-1]

    # END getDBName

    def extract(self, data_only=False):
        db_name = self.getDBName(self.db_url)

        # Get the metadata for the database
        con = self.getConnection(self.db_url)
        metadata = MetaData()
        metadata.reflect(bind=con, views=True)

        # Add top level elements for tables and columns
        elems = DataFrame(
            [
                {"id": "database table", "name": "database table", "type": ElementType.DATA_OBJECT},
                {
                    "id": "database table column",
                    "name": "database table column",
                    "type": ElementType.DATA_OBJECT,
                },
            ],
            columns=["id", "name", "type", "label"],
        )

        # A table is a set of columns, so add an aggregation relationship between table and column
        rels = DataFrame(
            [
                {
                    "id": "database_table column",
                    "type": RelationshipType.AGGREGATION,
                    "source": "database table",
                    "target": "database table column",
                    "name": "",
                }
            ],
            columns=["id", "name", "type", "label", "source", "target"],
        )

        # This is the model that will contain our generated schema
        model = ArchimateModel(
            f"created database schema: {db_name}",
            elems,
            rels,
            DataFrame(columns=["id", "name", "type", "nodes", "connections", "properties"]),
            DataFrame(),
            defaultAttributeMapping=True,
        )

        element_metadata = []

        # Add every table in the database to the model as a data object,
        # including the columns, and generate a view for each table added.
        for table_index, table in enumerate(metadata.sorted_tables):
            table_name = self.formatTableName(db_name, table.schema, table.name)

            # First, create a node representing the table
            nodes = [
                {"id": table_name, "name": table_name, "type": ElementType.DATA_OBJECT, "label": table_name}
            ]
            edges = [
                {
                    "id": "database_table" + str(table_index),
                    "type": RelationshipType.SPECIALIZATION,
                    "source": table_name,
                    "target": "database table",
                    "name": "",
                    "label": "",
                }
            ]

            columns = list(table.columns)

            # Next, create a node for every column in the table
            for column_index, column in enumerate(columns):
                name = f"{table_name}.{column.name}"
                nodes.append(
                    {
                        "id": name,
                        "name": name,
                        "type": ElementType.DATA_OBJECT,
                        "label": name,
                        "db_dataType": str(column.type),
                        "db_nullable": str(column.nullable is True),
                    }
                )
                edges.append(
                    {
                        "id": table_name + str(column_index),
                        "type": RelationshipType.AGGREGATION,
                        "source": table_name,
                        "target": name,
                        "name": "",
                        "label": "",
                    }
                )
                edges.append(
                    {
                        "id": "database_table column" + str(column_index),
                        "type": RelationshipType.SPECIALIZATION,
                        "source": name,
                        "target": "database table column",
                        "name": "",
                        "label": "",
                    }
                )
            # END LOOP

            # Add the generated concepts to the model
            model.nodes = model.nodes.append(nodes)
            model.edges = model.edges.append(edges)

            # Finally, generate a view containing the concepts related to the current table
            view = ArchimateUtils.generate_view(
                model,
                nodes=[node["id"] for node in nodes],
                edges=[edge["id"] for edge in edges],
                name=table_name,
                layout=LayoutEnum.HIERARCHICAL,
                node_height=100,
            )

            concept_metadata = [
                {"id": concept["id"], "data": {"original_id": concept["id"], "created_by": self.script_name}}
                for concept in (nodes + edges)
            ]

            view_metadata = {
                "id": view[model.getViewAttributeMapping(ViewAttribute.ID)],
                "data": {
                    "original_id": view[model.getViewAttributeMapping(ViewAttribute.ID)],
                    "created_by": self.script_name,
                },
            }
            element_metadata.extend(concept_metadata)
            element_metadata.append(view_metadata)
        # END LOOP

        # Add the generated concepts to the model organization
        model.organize()

        return ExtractionResult(model, element_metadata, self.branch_name)

    # END extract


# END DBExtractor
