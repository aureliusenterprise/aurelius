import json
import re

from sqlalchemy import Table, select


class AbstractSlice:
    VIZ_TYPE = None

    def __init__(
        self,
        db_con=None,
        db_metadata=None,
        created_on=None,
        changed_on=None,
        id=None,
        slice_name=None,
        datasource_type=None,
        datasource_name=None,
        viz_type=None,
        params=None,
        created_by_fk=None,
        changed_by_fk=None,
        description=None,
        cache_timeout=None,
        perm=None,
        datasource_id=None,
        druid_datasource_id=None,
        table_id=None,
    ):
        self.db_con = db_con
        self.db_metadata = db_metadata

        self.created_on = created_on
        self.changed_on = changed_on
        self.id = id
        self.slice_name = slice_name
        self.datasource_type = datasource_type
        self.viz_type = viz_type
        self.params = params
        self.created_by_fk = created_by_fk
        self.changed_by_fk = changed_by_fk
        self.description = description
        self.cache_timeout = cache_timeout
        self.perm = perm
        self.datasource_id = datasource_id
        self.druid_datasource_id = druid_datasource_id
        self.table_id = table_id

        self.metrics = []
        self.filters = []
        self.granularity_sqla = None
        self.having = ""
        self.where = ""

        self._init_params(**(json.loads(params)))  # type: ignore[reportGeneralTypeIssues]

    # END __init__

    def _init_params(**kwargs):
        pass

    # END _init_params

    def directColumnDependencies(self):
        table_columns_table = Table(
            "table_columns", self.db_metadata, autload=True, autoload_with=self.db_con
        )
        table_columns = [
            row
            for row in self.db_con.execute(  # type: ignore[reportOptionalSubscript, reportOptionalMemberAccess]
                select([table_columns_table]).where(
                    table_columns_table.c.table_id == self.datasource_id  # type: ignore[reportOptionalSubscript, reportOptionalMemberAccess]
                )
            )
        ]
        return [column[2] for column in table_columns if column[4] in self.columnNames()]

    # END directColumnDependencies

    def columnNames(self):
        return list(
            set(
                [column for metric in self.getMetrics() for column in self.columnsFromSQL(metric[7])]
                + [f["col"] for f in self.filters if f.get("col") is not None]
                + [self.granularity_sqla]
                + self.columnsFromSQL(self.having)
                + self.columnsFromSQL(self.where)
            )
        )

    def columnsFromSQL(self, sql):
        table_columns_table = Table(
            "table_columns", self.db_metadata, autload=True, autoload_with=self.db_con
        )
        table_columns = [
            row[4]
            for row in self.db_con.execute(  # type: ignore[reportOptionalSubscript, reportOptionalMemberAccess]
                select([table_columns_table]).where(
                    table_columns_table.c.table_id == self.datasource_id  # type: ignore[reportOptionalSubscript, reportOptionalMemberAccess]
                )
            )
        ]
        return [
            group for match in re.finditer("(\w+)", sql) for group in match.groups() if group in table_columns
        ]

    # END columnsFromSQL

    def getMetrics(self):
        table = Table("sql_metrics", self.db_metadata, autoload=True, autoload_with=self.db_con)
        data = self.db_con.execute(  # type: ignore[reportOptionalSubscript, reportOptionalMemberAccess]
            select([table]).where(table.c.table_id == self.datasource_id)  # type: ignore[reportOptionalSubscript, reportOptionalMemberAccess]
        ).fetchall()

        return [metric for metric in data if metric[3] in self.metrics]

    # END getMetrics


# END AbstractSlice
