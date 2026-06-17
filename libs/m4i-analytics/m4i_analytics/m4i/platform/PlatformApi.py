from __future__ import annotations

import numbers
from collections.abc import Sequence
from typing import IO, Any, Optional

import m4i_analytics.m4i.platform.config as config
from m4i_analytics.m4i.ApiUtils import ApiUtils, ContentType
from m4i_analytics.m4i.platform.model.Branch import Branch
from m4i_analytics.m4i.platform.model.DataRetrieve import DataRetrieve
from m4i_analytics.m4i.platform.model.MetricExemption import MetricExemption
from m4i_analytics.m4i.platform.model.ModelCommit import ModelCommit
from m4i_analytics.m4i.platform.model.ModelProvenance import ModelProvenance
from m4i_analytics.m4i.platform.model.Project import Project
from m4i_analytics.m4i.platform.model.UserRole import UserRole


class PlatformApi:
    """
    This class implements various API calls to functions provided by the M4I platform
    """

    @staticmethod
    def retrieve_project(
        projectid: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> Project:
        """
        Retrieve a project for the given ID from the M4I repository

        :returns: A Project instance representing the project with the given ID
        :rtype: Project

        :param str projectid: The ID of the project you wish to retrieve

        :exception TypeError: Thrown when projectid is not defined or when the query
        result could not be parsed into a ModelCommit instance.
        :exception ValueError: Thrown when projectid is not valid or when the query
        result could otherwise not be parsed.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if projectid is None:
            raise TypeError("Projectid is not defined")
        elif not isinstance(projectid, str):
            raise ValueError("Projectid should be a string")

        result = ApiUtils.get(
            f"{config.PROJECT_DETAILS_ENDPOINT}{projectid}",
            content_type=ContentType.JSON,
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        assert isinstance(result, dict), f"Expected dict for project details, got {type(result)}"
        return Project(**result)

    # END retrieve_project

    @staticmethod
    def retrieve_model(
        branchName: str,
        projectName: str,
        userid: str,
        contentType: str = "archimate",
        modelid: str = "TRUNK",
        module: Optional[str] = None,
        withViews: bool = True,
        parserName: str = "archimate3",
        version: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> str:
        """
        Retrieve a model with the given parameters from the M4I repository.

        :returns: A string representation of the model that fits the parameters, parsed
        to the specified content type (archimate by default).
        :rtype: str

        :param str branchName: The name of the branch containing the model you wish to
        retrieve.
        :param str projectName: The name of the project containing the model you wish to
        retrieve.
        :param str userid: The id of the user retrieving the model.
        :param str contentType: *Optional*. The format in which you wish to retrieve the
        model. Valid options are: 'archimate', 'json' and 'xml'. Default is 'archimate'.
        :param str modelid: *Optional*. The id of the model you wish to retrieve. You
        can use this e.g. to retrieve a version of a model before conflicts were
        resolved. Default is 'TRUNK'.
        :param str module: *Optional*. The name of the module you wish to retrieve. By
        leaving this empty, you retrieve the whole model. Default is empty.
        :param str parserName: *Optional*. The name of the meta-model of the model you
        wish to retrieve. Currently, the only valid option is 'archimate3'. Default is
        'archimate3'.
        :param boolean withViews: *Optional*. Indicating whether the retrieved model
        should contain views. For analysis of the model, the views are often not used
        for analysis, thus can be omitted when downloading the model.
        :param long version: *Optional*. The timestamp of the version of the model you
        wish to retrieve. By leaving this empty, you retrieve the latest version.
        Default is empty.

        :exception TypeError: Thrown when any of the parameters (excluding module and
        version) is not defined.
        :exception ValueError: Thrown when any of the parameters is not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if branchName is None:
            raise TypeError("BranchName is not defined")
        elif not isinstance(branchName, str):
            raise ValueError("BranchName should be a string")
        elif projectName is None:
            raise TypeError("ProjectName is not defined")
        elif not isinstance(projectName, str):
            raise ValueError("ProjectName should be a string")
        elif userid is None:
            raise TypeError("Userid is not defined")
        elif not isinstance(userid, str):
            raise ValueError("Userid should be a string")
        elif contentType is None:
            raise ValueError("ContentType is not defined")
        elif not isinstance(contentType, str):
            raise ValueError("ContentType should be a string")
        elif modelid is None:
            raise TypeError("Modelid is not defined")
        elif not isinstance(modelid, str):
            raise ValueError("Modelid should be a string")
        elif module is not None and not isinstance(module, str):
            raise ValueError("Module should be a string")
        elif parserName is None:
            raise TypeError("ParserName is not defined")
        elif not isinstance(parserName, str):
            raise ValueError("ParserName should be a string")
        elif version is not None and not isinstance(version, numbers.Integral):
            raise ValueError("Version should be a long")

        result = ApiUtils.get(
            config.RETRIEVE_MODEL_ENDPOINT,
            content_type=ContentType.BINARY,
            params={
                "branchName": branchName,
                "contentType": contentType,
                "modelId": modelid,
                "module": module,
                "parserName": parserName,
                "projectName": projectName,
                "userid": userid,
                "withViews": withViews,
                "version": version,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        assert isinstance(result, str), f"Expected str response for model, got {type(result)}"
        return result

    # END retrieve_model

    @staticmethod
    def commit_model(
        branchName: str,
        projectName: str,
        userid: str,
        description: str,
        modelId: str,
        model: IO[Any],
        contentType: str = "archimate",
        module: Optional[str] = None,
        parserName: str = "archimate3",
        username: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> ModelCommit:
        """
        Commit a model to the M4I repository.

        :returns: A ModelCommit instance describing the commit operation. Note that the
        commit happens asynchronously on the server side. You can monitor the progress
        via query_model requests.
        :rtype: ModelCommit

        :param str branchName: The name of the branch to which you want to commit the
        model.
        :param str projectName: The name of the project to which you want to commit the
        model.
        :param str userid: The id of the user committing the model.
        :param str description: Describe the purpose of your commit.
        :param file model: The file containing your model.
        :param str contentType: *Optional*. The format in which you are committing the
        model. Valid options are: 'archimate', 'json' and 'xml'. Default is 'archimate'.
        :param str module: *Optional*. The name of the module to which you want to
        commit. You can also define new modules this way. By leaving this empty, you
        commit to the complete model. Default is empty.
        :param str parserName: *Optional*. The name of the meta-model of the model you
        are committing. Currently, the only valid option is 'archimate3'. Default is
        'archimate3'.

        :exception TypeError: Thrown when any of the parameters (excluding module) is
        not defined or when the query result could not be parsed into a ModelCommit
        instance.
        :exception ValueError: Thrown when any of the parameters is not valid or when
        the query result could otherwise not be parsed.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if branchName is None:
            raise TypeError("BranchName is not defined")
        elif not isinstance(branchName, str):
            raise ValueError("BranchName should be a string")
        elif projectName is None:
            raise TypeError("ProjectName is not defined")
        elif not isinstance(projectName, str):
            raise ValueError("ProjectName should be a string")
        elif userid is None:
            raise TypeError("Userid is not defined")
        elif not isinstance(userid, str):
            raise ValueError("Userid should be a string")
        elif description is None:
            raise TypeError("Description is not defined")
        elif not isinstance(description, str):
            raise ValueError("Description should be a string")
        elif modelId is None:
            raise TypeError("ModelId is not defined")
        elif not isinstance(modelId, str):
            raise ValueError("ModelId should be a string")
        elif model is None:
            raise TypeError("Model is not defined")
        elif contentType is None:
            raise TypeError("ContentType is not defined")
        elif not isinstance(contentType, str):
            raise ValueError("ContentType should be a string")
        elif module is not None and not isinstance(module, str):
            raise ValueError("Module should be a string")

        result = ApiUtils.post_file(
            config.COMMIT_MODEL_ENDPOINT,
            content_type=ContentType.JSON,
            file=model,
            data={
                "parserName": parserName,
                "toBranchName": branchName,
                "projectName": projectName,
                "userid": userid,
                "comment": description,
                "modelId": modelId,
                "contentType": contentType,
                "module": module,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        assert isinstance(result, dict), f"Expected dict for model commit, got {type(result)}"
        return ModelCommit(**result)

    # END commit_model

    @staticmethod
    def query_model(
        projectName: str,
        taskid: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> Any:
        """
        Check on the progress of a commit to the M4I repository. This request will tell
        you whether the commit is still in progress, completed, has encountered a
        conflict, or has failed for some other reason. You can use this function for
        both commit_model, clone_branch and commit_branch.

        :returns: A ModelQuery instance describing the status of the commit operation.
        If the commit encountered conflicts, the response will also include a list of
        all the conflicting changes.
        :rtype: ModelQuery

        :param str projectName: The name of the project to which are committing the
        model.
        :param str taskid: The id of the commit operation.

        :exception TypeError: Thrown when any of the parameters is not defined or when
        the query result could not be parsed into a ModelQuery instance.
        :exception ValueError: Thrown when any of the parameters is not valid or when
        the query result could otherwise not be parsed.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if projectName is None:
            raise TypeError("ProjectName is not defined")
        elif not isinstance(projectName, str):
            raise ValueError("ProjectName should be a string")
        elif taskid is None:
            raise TypeError("Taskid is not defined")
        elif not isinstance(taskid, str):
            raise ValueError("Taskid should be a string")

        result = ApiUtils.get(
            config.QUERY_MODEL_ENDPOINT,
            content_type=ContentType.JSON,
            params={"projectName": projectName, "taskId": taskid},
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        return result

    # END query_model

    @staticmethod
    def model_provenance(
        projectName: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        #                          "branchName: "+branchName);
        # 		LOGGER.info("pageLength: "+pageLength);
        # 		LOGGER.info("pageOffset: "+pageOffset);
        # 		LOGGER.info("query: "+query);
        # 		LOGGER.info("latestOnly: "+latestOnly);
        # 		LOGGER.info("startDate: "+startDate);
        # 		LOGGER.info("endDate: "+endDate)
        """
        Retrieve a historic list of all operations on the model over time.

        :returns: An array containing ModelProvenance instances, describing historic
        events that occurred for the specified model.
        :rtype: array<ModelProvenance>

        :param str projectName: The name of the project for which you want to retrieve
        the provenance.

        :exception TypeError: Thrown when projectName is not defined or when the query
        response could not be parsed into ModelProvenance instances.
        :exception ValueError: Thrown when projectName is not valid or when the query
        response could otherwise not be parsed.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if projectName is None:
            raise TypeError("ProjectName is not defined")
        elif not isinstance(projectName, str):
            raise ValueError("ProjectName should be a string")

        result = ApiUtils.get(
            config.MODEL_PROVENANCE_ENDPOINT,
            content_type=ContentType.JSON,
            params={"projectName": projectName},
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        if isinstance(result, list):
            result = map(lambda i: ModelProvenance(**i), result)
        else:
            raise ValueError("Query response is not a list")

        return result

    # END model_provenance

    @staticmethod
    def clone_branch(
        description: str,
        projectName: str,
        toBranch: str,
        userid: str,
        fromBranch: str = "MASTER",
        parserName: str = "archimate3",
        username: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> ModelCommit:
        """
        Clone an existing branch of your model into a new branch.

        :returns: A ModelCommit instance describing the clone operation. Note that the
        clone happens asynchronously on the server side. You can monitor the progress
        via query_model requests.
        :rtype: ModelCommit

        :param str description: Describe the purpose of this new branch.
        :param str projectName: The name of the project for which you want to clone
        branches.
        :param str toBranch: The name of your new branch.
        :param str userid: The name of the user creating the new branch.
        :param str fromBranch: *Optional*. The name of the branch you wish to clone.
        Default is 'MASTER'.
        :param str parserName: *Optional*. The name of the meta-model of the model that
        will be contained in your new branch. Currently, the only valid option is
        'archimate3'. Default is 'archimate3'.

        :exception TypeError: Thrown when any of the parameters is not defined or when
        the query result could not be parsed into a ModelCommit instance.
        :exception ValueError: Thrown when any of the parameters is not valid or when
        the query result could otherwise not be parsed.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if description is None:
            raise TypeError("Description is not defined")
        elif not isinstance(description, str):
            raise ValueError("Description should be a string")
        elif fromBranch is None:
            raise TypeError("FromBranch is not defined")
        elif not isinstance(fromBranch, str):
            raise ValueError("FromBranch should be a string")
        elif projectName is None:
            raise TypeError("ProjectName is not defined")
        elif not isinstance(projectName, str):
            raise ValueError("ProjectName should be a string")
        elif toBranch is None:
            raise TypeError("ToBranch is not defined")
        elif not isinstance(toBranch, str):
            raise ValueError("ToBranch should be a string")
        elif userid is None:
            raise TypeError("Userid is not defined")
        elif not isinstance(userid, str):
            raise ValueError("Userid should be a string")
        elif parserName is None:
            raise TypeError("ParserName is not defined")
        elif not isinstance(parserName, str):
            raise ValueError("ParserName should be a string")

        result = ApiUtils.post(
            config.CLONE_BRANCH_ENDPOINT,
            content_type=ContentType.JSON,
            data={
                "comment": description,
                "fromBranch": fromBranch,
                "parserName": parserName,
                "projectName": projectName,
                "toBranch": toBranch,
                "userid": userid,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        assert isinstance(result, dict), f"Expected dict for clone_branch result, got {type(result)}"
        return ModelCommit(**result)

    # END clone_branch

    @staticmethod
    def commit_branch(
        description: str,
        fromBranch: str,
        projectName: str,
        toBranch: str,
        userid: str,
        parserName: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> ModelCommit:
        """
        Merge one of the branches of your model with another branch of your model,
        applying the changes in either to both.

        :returns: A ModelCommit instance describing the commit operation. Note that the
        commit happens asynchronously on the server side. You can monitor the progress
        via query_model requests.
        :rtype: ModelCommit

        :param str description: Describe the purpose of merging the branches.
        :param str projectName: The name of the project for which you want to merge
        branches.
        :param str toBranch: The name of the target branch.
        :param str userid: The name of the user creating the new branch.
        :param str fromBranch: The name of the source branch.
        :param str parserName: *Optional*. The name of the meta-model of the model that
        is contained in the target branch. Currently, the only valid option is
        'archimate3'. Default is 'archimate3'.

        :exception TypeError: Thrown when any of the parameters is not defined or when
        the query result could not be parsed into a ModelCommit instance.
        :exception ValueError: Thrown when any of the parameters is not valid or when
        the query result could otherwise not be parsed.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if description is None:
            raise TypeError("Description is not defined")
        elif not isinstance(description, str):
            raise ValueError("Description should be a string")
        elif fromBranch is None:
            raise TypeError("FromBranch is not defined")
        elif not isinstance(fromBranch, str):
            raise ValueError("FromBranch should be a string")
        elif projectName is None:
            raise TypeError("ProjectName is not defined")
        elif not isinstance(projectName, str):
            raise ValueError("ProjectName should be a string")
        elif toBranch is None:
            raise TypeError("ToBranch is not defined")
        elif not isinstance(toBranch, str):
            raise ValueError("ToBranch should be a string")
        elif userid is None:
            raise TypeError("Userid is not defined")
        elif not isinstance(userid, str):
            raise ValueError("Userid should be a string")
        elif parserName is None:
            raise TypeError("ParserName is not defined")
        elif not isinstance(parserName, str):
            raise ValueError("ParserName should be a string")

        result = ApiUtils.post(
            config.COMMIT_BRANCH_ENDPOINT,
            content_type=ContentType.JSON,
            data={
                "comment": description,
                "fromBranch": fromBranch,
                "parserName": parserName,
                "projectName": projectName,
                "toBranch": toBranch,
                "userid": userid,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        assert isinstance(result, dict), f"Expected dict for commit_branch result, got {type(result)}"
        return ModelCommit(**result)

    # END commit_branch

    @staticmethod
    def force_commit(
        addListLeft: list[str],
        addListRight: list[str],
        description: str,
        deleteListLeft: list[str],
        deleteListRight: list[str],
        fromBranch: str,
        fromModelId: str,
        projectName: str,
        taskid: str,
        toBranch: str,
        toModelId: str,
        userid: str,
        template: str,
        contentType: str = "archimate",
        module: str = "",
        parserName: str = "archimate3",
        username: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> ModelCommit:
        """
        Commit a version of your model to the repository, and resolve any conflicts
        according to the provided parameters.

        :returns: A ModelCommit instance describing the commit operation. Note that the
        commit happens asynchronously on the server side. You can monitor the progress
        via query_model requests.
        :rtype: ModelCommit

        :param array<str> addListLeft: If there is a version conflict, and you wish to
        keep a particular newly added or otherwise modified element from the repository,
        you add the ID of that element to this list.
        :param array<str> addListRight: If there is a version conflict, and you wish to
        keep a particular newly added or otherwise modified element from committed
        model, you add the ID of that element to this list.
        :param str description: Describe the purpose of the commit.
        :param array<str> deleteListLeft: If there is a version conflict, and you wish
        to delete a particular element from the repository, you add the ID of that
        element to this list.
        :param array<str> deleteListRight: If there is a version conflict, and you wish
        to delete a particular element from the committed model, you add the ID of that
        element to this list.
        :param fromBranch: The name of the source branch.
        :param str fromModelId: The id of the model you wish to merge from. You can use
        this e.g. to merge from a version of a model before conflicts were resolved.
        :param str projectName: The name of the project for which you want to do a
        commit.
        :param str taskid: The id of the commit operation.
        :param str toBranch: The name of the target branch. To do a commit within a
        branch, keep this the same as fromBranch.
        :param str toModelId: The id of the model you wish to merge to. You can use this
        e.g. to merge towards a version of a model before conflicts were resolved.
        :param str userid: The name of the user creating the new branch.
        :param str contentType: *Optional*. The format in which you are committing the
        model. Valid options are: 'archimate', 'json' and 'xml'. Default is 'archimate'.
        :param str module: *Optional*. The name of the module to which you want to
        commit. You can also define new modules this way. By leaving this empty, you
        commit to the complete model. Default is empty.
        :param str parserName: *Optional*. The name of the meta-model of the model that
        is contained in the target branch. Currently, the only valid option is
        'archimate3'. Default is 'archimate3'.

        :exception TypeError: Thrown when any of the parameters (other than module) is
        not defined or when the query result could not be parsed into a ModelCommit
        instance.
        :exception ValueError: Thrown when any of the parameters is not valid or when
        the query result could otherwise not be parsed.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if addListLeft is None:
            raise TypeError("AddListLeft is not defined")
        elif not isinstance(addListLeft, list):
            raise ValueError("AddListLeft should be an array")
        elif addListRight is None:
            raise TypeError("AddListRight is not defined")
        elif not isinstance(addListRight, list):
            raise ValueError("AddListRight should be an array")
        elif description is None:
            raise TypeError("Description is not defined")
        elif not isinstance(description, str):
            raise ValueError("Description should be a string")
        elif deleteListLeft is None:
            raise TypeError("DeleteListLeft is not defined")
        elif not isinstance(deleteListLeft, list):
            raise ValueError("DeleteListLeft should be an array")
        elif deleteListRight is None:
            raise TypeError("DeleteListRight is not defined")
        elif not isinstance(deleteListRight, list):
            raise ValueError("DeleteListRight should be an array")
        elif fromBranch is None:
            raise TypeError("FromBranch is not defined")
        elif not isinstance(fromBranch, str):
            raise ValueError("FromBranch should be a string")
        elif fromModelId is None:
            raise TypeError("FromModelId is not defined")
        elif not isinstance(fromModelId, str):
            raise ValueError("FromModelId should be a string")
        elif projectName is None:
            raise TypeError("ProjectName is not defined")
        elif not isinstance(projectName, str):
            raise ValueError("ProjectName should be a string")
        elif taskid is None:
            raise TypeError("Taskid is not defined")
        elif not isinstance(taskid, str):
            raise ValueError("Taskid should be a string")
        elif toBranch is None:
            raise TypeError("ToBranch is not defined")
        elif not isinstance(toBranch, str):
            raise ValueError("ToBranch should be a string")
        elif toModelId is None:
            raise TypeError("ToModelId is not defined")
        elif not isinstance(toModelId, str):
            raise ValueError("ToModelId should be a string")
        elif userid is None:
            raise TypeError("Userid is not defined")
        elif not isinstance(userid, str):
            raise ValueError("Userid should be a string")
        elif template is None:
            raise TypeError("Template is not defined")
        elif not isinstance(template, str):
            raise ValueError("Template should be a string")
        elif contentType is None:
            raise TypeError("ContentType is not defined")
        elif not isinstance(contentType, str):
            raise ValueError("ContentType should be a string")
        elif module is None:
            raise TypeError("Module is not defined")
        elif module is not None and not isinstance(module, str):
            raise ValueError("Module should be a string")
        elif parserName is None:
            raise TypeError("ParserName is not defined")
        elif not isinstance(parserName, str):
            raise ValueError("ParserName should be a string")

        result = ApiUtils.post(
            config.FORCE_COMMIT_MODEL_ENDPOINT,
            content_type=ContentType.JSON,
            data={
                "addListLeft": addListLeft,
                "addListRight": addListRight,
                "comment": description,
                "commitTaskId": taskid,
                "contentType": contentType,
                "deleteListLeft": deleteListLeft,
                "deleteListRight": deleteListRight,
                "fromBranchName": fromBranch,
                "fromModelId": fromModelId,
                "module": module,
                "parserName": parserName,
                "projectName": projectName,
                "toBranchName": toBranch,
                "toModelId": toModelId,
                "userid": userid,
                "template": template,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        assert isinstance(result, dict), f"Expected dict for force_commit result, got {type(result)}"
        return ModelCommit(**result)

    # END force_commit

    @staticmethod
    def data_upload(
        projectName: str,
        branchName: str,
        modelId: str,
        content: list[dict[str, Any]],
        username: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> str:
        """
        Upload concept attributes as key-value pairs to the repository. Note that, if a
        property already exists under the same key, the value of that property will be
        overriden.

        :returns: A string representing whether or not the upload completed successfully
        :rtype: str

        :param str projectName: The fully qualified name of the project as can be
        retrieved from the repository. You need to supply either this, or the project
        owner and the project name. Defaults to None.
        :param str branchName: The name of the branch to which these properties belong.
        Defaults to 'MASTER'.
        :param str modelId: The id of the model you wish to attach the properties to.
        Default is 'TRUNK'.
        :param list content: A list of dictionaries representing the properties that
        should be added to concepts in the model. Each dict is structured like this:

            {
                'id': concept id
                'data': {
                     key: value,
                     key: value
                }
            }
        """

        if projectName is None:
            raise TypeError("ProjectName is not defined")
        elif not isinstance(projectName, str):
            raise ValueError("ProjectName should be a string")
        elif branchName is None:
            raise TypeError("BranchName is not defined")
        elif not isinstance(branchName, str):
            raise ValueError("BranchName should be a string")
        elif modelId is None:
            raise TypeError("ModelId is not defined")
        elif not isinstance(modelId, str):
            raise ValueError("ModelId should be a string")
        elif content is None:
            raise TypeError("Content is not defined")
        elif not isinstance(content, list):
            raise ValueError("Content should be a string")

        result = ApiUtils.post_json(
            config.DATA_UPLOAD_ENDPOINT,
            content_type=ContentType.TEXT,
            data={"project": projectName, "branch": branchName, "model_id": modelId, "content": content},
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        assert isinstance(result, str), f"Expected str for data_upload result, got {type(result)}"
        return result

    # END data_upload

    @staticmethod
    def data_retrieve(
        project_name: str,
        branch_name: str,
        modelId: str,
        parser_name: str = "archimate3",
        username: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> DataRetrieve:
        """
        Retrieve data associated with concepts in a model from the repository

        :returns: An object containing a list of properties representing the data
        associated with the model
        :rtype: DataRetrieve

        :param str project_name: The fully qualified name of the project as can be
        retrieved from the repository. You need to supply either this, or the project
        owner and the project name. Defaults to None.
        :param str branch_name: The name of the branch to which these properties belong.
        Defaults to 'MASTER'.
        :param str modelId: The id of the model you wish to attach the properties to.
        Default is 'TRUNK'.
        :param str parser_name: *Optional*. The name of the meta-model of the model you
        wish to retrieve. Currently, the only valid option is 'archimate3'. Default is
        'archimate3'.
        """

        if project_name is None:
            raise TypeError("ProjectName is not defined")
        elif not isinstance(project_name, str):
            raise ValueError("ProjectName should be a string")
        elif branch_name is None:
            raise TypeError("BranchName is not defined")
        elif not isinstance(branch_name, str):
            raise ValueError("BranchName should be a string")
        elif modelId is None:
            raise TypeError("ModelId is not defined")
        elif not isinstance(modelId, str):
            raise ValueError("ModelId should be a string")
        elif parser_name is None:
            raise TypeError("ParserName is not defined")
        elif not isinstance(parser_name, str):
            raise ValueError("ParserName should be a string")

        result = ApiUtils.get(
            config.DATA_RETRIEVE_ENDPOINT,
            content_type=ContentType.JSON,
            params={
                "parserName": parser_name,
                "projectName": project_name,
                "branchName": branch_name,
                "modelId": modelId,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        assert isinstance(result, dict), f"Expected dict for data_retrieve result, got {type(result)}"
        return DataRetrieve(**result)

    # END data_retrieve

    @staticmethod
    def get_metric_exemptions(project_id: str, **kwargs):
        """
        Retrieves all `MetricExemption` for the project with the given `project_id`.
        You can optionally supply a `branch_id`, `metric_name` and `version` timestamp
        to limit the results.

        :returns: An list of all matching `MetricExemption`.
        :rtype: list of MetricExemption

        :param str project_id: The fully qualified name of the project as can be
        retrieved from the repository. You need to supply either this, or the project
        owner and the project name. Defaults to None.
        :param str branch_id: *Optional*. You can specify the branch id if you only want
        the exemptions for a particular branch.
        :param str metric_name: *Optional*. You can specify a metric name if you want to
        limit the exemptions to the metric with that name.
        :param number version: *Optional*. You can specify the version timestamp if you
        only want the exemptions for a particular version.
        """

        if project_id is None:
            raise TypeError("project_id is not defined")
        # END IF

        result = ApiUtils.get(
            config.EXEMPTIONS_ENDPOINT,
            content_type=ContentType.JSON,
            params={
                "project_id": project_id,
                "branch": kwargs.get("branch_id"),
                "metric": kwargs.get("metric_name"),
                "version": kwargs.get("version"),
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=kwargs.get("username"),
            password=kwargs.get("password"),
            totp=kwargs.get("totp"),
            access_token=kwargs.get("access_token"),
        )

        assert isinstance(result, list), f"Expected list for metric exemptions, got {type(result)}"
        return [MetricExemption(**exemption) for exemption in result]

    # END get_metric_exemptions

    @staticmethod
    def create_metric_exemption(exemption: MetricExemption, **kwargs: Any) -> MetricExemption:
        """
        Commits the given `MetricExemption` in the database.

        :returns: The `MetricExemption` as it exists in the database.
        :rtype: MetricExemption

        :param str exemption: The exemption which should be committed to the database.
        """
        if exemption is None:
            raise TypeError("exemption is not defined")
        # END IF

        result = ApiUtils.post_json(
            config.EXEMPTIONS_ENDPOINT,
            content_type=ContentType.JSON,
            data=exemption.toJSON(),  # type: ignore[reportGeneralTypeIssues]
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=kwargs.get("username"),
            password=kwargs.get("password"),
            totp=kwargs.get("totp"),
            access_token=kwargs.get("access_token"),
        )

        assert isinstance(result, dict), (
            f"Expected dict for create_metric_exemption result, got {type(result)}"
        )
        return MetricExemption(**result)

    # END create_metric_exemption

    @staticmethod
    def update_metric_exemption(exemption: MetricExemption, **kwargs: Any) -> MetricExemption:
        """
        Commits the given `MetricExemption` in the database.

        The behavior of this function is identical to
        `PlatformApi.create_metric_exemption`.

        :returns: The `MetricExemption` as it exists in the database.
        :rtype: MetricExemption

        :param str exemption: The exemption which should be committed to the database.
        """

        return PlatformApi.create_metric_exemption(exemption, **kwargs)

    # END update_metric_exemption

    @staticmethod
    def delete_metric_exemption(exemption_id: str, metric_name: str, project_id: str, **kwargs: Any) -> None:
        """
        Deletes the `MetricExemption` which matches the given `exemption_id`,
        `metric_name` and `project_id` from the database.

        :param exemption_id: The id of the exemption which should be deleted
        :param metric_name: The name of the metric to which the exemption belongs
        :param project_id: The id of the project to which the exemption belongs
        """

        if exemption_id is None:
            raise TypeError("exemption_id is not defined")
        # END IF
        if metric_name is None:
            raise TypeError("metric_name is not defined")
        # END IF
        if project_id is None:
            raise TypeError("project_id is not defined")
        # END IF

        ApiUtils.delete(
            f"{config.EXEMPTIONS_ENDPOINT}/{metric_name}/{project_id}/{exemption_id}",
            content_type=ContentType.JSON,
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=kwargs.get("username"),
            password=kwargs.get("password"),
            totp=kwargs.get("totp"),
            access_token=kwargs.get("access_token"),
        )

    # END delete_metric_exemption

    @staticmethod
    def get_branches(project_id: str, **kwargs: Any) -> Sequence[Branch]:
        """
        Retrieves the branches for the project with the given id

        :raises TypeError: if the project id is not defined
        :return: A list of branches belonging to the project with the given id
        :rtype: Sequence[Branch]
        """

        if project_id is None:
            raise TypeError("project_id is not defined")
        # END IF

        result = ApiUtils.get(
            f"{config.REPOSITORY_BASE_URI}project/branch",
            params={"project_id": project_id},
            content_type=ContentType.JSON,
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=kwargs.get("username"),
            password=kwargs.get("password"),
            totp=kwargs.get("totp"),
            access_token=kwargs.get("access_token"),
        )

        assert isinstance(result, list), f"Expected list for branches, got {type(result)}"
        return [Branch(**branch) for branch in result]

    # END get_branches

    @staticmethod
    def get_user_role(project_name: str, **kwargs: Any) -> UserRole:
        """
        Retrieves role of the user in the project with the given name. Needs some form
        of user authentication parameters to work (i.e. username/password or access
        token)

        :raises TypeError: if the project name is not defined
        :return: The role of the user the project with the given name as a number 0-5
        :rtype: int
        """

        if project_name is None:
            raise TypeError("project_name is not defined")
        # END IF

        result = ApiUtils.get(
            f"{config.REPOSITORY_BASE_URI}auth/role/{project_name}",
            content_type=ContentType.JSON,
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
            username=kwargs.get("username"),
            password=kwargs.get("password"),
            totp=kwargs.get("totp"),
            access_token=kwargs.get("access_token"),
        )

        assert isinstance(result, dict), f"Expected dict for user role, got {type(result)}"
        return UserRole(**result)

    # END get_user_role


# END PlatformApi
