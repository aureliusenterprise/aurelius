import logging

from elasticsearch import NotFoundError
from elasticsearch.helpers import scan
from pandas import DataFrame

from .utils import make_elastic_connection

QUERY = {
    "query": {
        "match_all": {}
    }
}

log = logging.getLogger(__name__)


def retrieve_elastic_data(
    index_name: str,
    query: str = QUERY,
) -> DataFrame:
    """
    Retrieves the data from the given elastic index as a Pandas DataFrame.
    You have the option to specify the query and the length of each page retrieved.
    """

    connection = make_elastic_connection()

    result = DataFrame()

    try:
        search_results = scan(
            client=connection,
            query=query,
            index=index_name
        )

        documents = map(lambda hit: hit['_source'], search_results)

        result = DataFrame(documents)
    except NotFoundError as e:
        log.exception(e)
    finally:
        connection.close()
    # END TRY

    return result
# END retrieve_elastic_data
