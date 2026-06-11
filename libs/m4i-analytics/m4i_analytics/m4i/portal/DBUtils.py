from enum import Enum

from pandas import read_sql_table
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm.session import sessionmaker

import m4i_analytics.m4i.portal.config as config


class M4I_DB_Connector:
    M4I_DB = create_engine(config.SQLALCHEMY_URL, pool_recycle=config.DB_CONNECTION_LIFETIME)


# END M4I_DB_CONNECTOR


class InsertBehavior(Enum):
    FAIL = "fail"
    REPLACE = "replace"
    APPEND = "append"


# END InsertBehavior


class DBUtils:
    @staticmethod
    def read_dataset(tablename):
        """
        Read the contents of a table into a pandas DataFrame.
        :rtype: pandas.DataFrame
        :return: A DataFrame containing the data read from the table

        :param tablename: The name of the table you wish to read from
        """

        with M4I_DB_Connector.M4I_DB.begin() as conn:
            result = read_sql_table(tablename, conn)
        return result

    # END read_dataset

    @staticmethod
    def insert_dataset(
        dataframe, tablename, schema=None, session=None, commit=True, if_exists=InsertBehavior.APPEND
    ):
        """
        Insert a dataframe into the given table in the M4I database.
        You have the option to create a new table if the one specified
        does not yet exist.

        :rtype: None

        :param DataFrame dataframe: The dataframe containing the records
            you wish to insert.
        :param str tablename: The name of the table into which you wish
            to insert the data.
        :param InsertBehavior if_exists: *Optional*. Specifies the
            behavior when the specified table already exists in the
            database. Defaults to InsertBehavior.FAIL.

        :exception ValueError: Thrown when the insert behavior is set
            to fail and the selected table already exists in the
            database.
        """

        # Inserts dataframe to database table

        # If no session has been created, set up a new one and commit the transaction
        if not session:
            sm = sessionmaker(bind=M4I_DB_Connector.M4I_DB)
            session = sm()
            commit = True

        _metadata = MetaData(bind=M4I_DB_Connector.M4I_DB)

        _list_of_dicts = dataframe.to_dict(orient="records")

        try:
            with M4I_DB_Connector.M4I_DB.begin() as conn:
                if not M4I_DB_Connector.M4I_DB.dialect.has_table(M4I_DB_Connector.M4I_DB, tablename):
                    dataframe.to_sql(tablename, conn)
                else:
                    if if_exists == InsertBehavior.FAIL:
                        dataframe.to_sql(name=tablename, con=conn, if_exists="fail")
                    if if_exists == InsertBehavior.REPLACE:
                        dataframe.to_sql(name=tablename, con=conn, if_exists="replace")
                    if if_exists == InsertBehavior.APPEND:
                        dataframe.to_sql(name=tablename, con=conn, if_exists="append")

            if commit:
                # leave it to the parent procedure to commit
                session.commit()
        except Exception as e:
            print(e)
            if commit:
                # leave it to the parent procedure to rollback
                session.rollback()

    # END insert_dataset


# END DBUtils
