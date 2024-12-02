import logging

from pandas import DataFrame

from .utils import make_elastic_connection

log = logging.getLogger(__name__)


def index_elastic_data(data: DataFrame, index: str):
    """
    Writes the given data to the Elasticsearch index with the given name.
    Uses the index of the rows as ids.
    """

    elastic = make_elastic_connection()

    try:
        for id, row in data.iterrows():
            body = row.to_dict()

            response = elastic.index(
                index=index,
                id=str(id),
                body=body
            )

            log.debug(response)
        # END LOOP
    except Exception as e:
        log.exception(e)
    finally:
        elastic.close()
    # END TRY
# END index_elastic_data
