import m4i_analytics.m4i.nifi.config as config
from m4i_analytics.m4i.ApiUtils import ApiUtils, ContentType
from m4i_analytics.m4i.nifi.model.ObjectModel import (
    ProcessGroupFlowEntity,
)


class NifiApi:
    @staticmethod
    def retrieve_process_group(name):
        if name is None:
            raise TypeError("Name should not be undefined")
        elif not isinstance(name, str):
            raise ValueError("Name should be a string")

        result = ApiUtils.get(config.FLOW_PROCESS_GROUPS_ENDPOINT + name, content_type=ContentType.JSON)

        assert isinstance(result, dict), f"Expected dict for retrieve_process_group, got {type(result)}"
        return ProcessGroupFlowEntity(**result)

    # END retrieve_process_group


# END NifiApi
