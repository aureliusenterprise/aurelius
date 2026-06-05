import time
from enum import Enum

from m4i_analytics.m4i.M4IUtils import M4IUtils
from m4i_analytics.m4i.platform.model.ModelQuery import StateEnum as ModelQueryStateEnum
from m4i_analytics.m4i.platform.model.ModelQueryDifResult import (
    StateEnum as ModelQueryDifResultStateEnum,
)
from m4i_analytics.m4i.platform.PlatformApi import PlatformApi


class ConflictResolutionTemplate(Enum):
    """
    This class enumerates the various conflict resolution templates supported by the repository
    """

    REPOSITORY_ONLY = "repository_only"
    UPLOAD_ONLY = "upload_only"
    UNION_REPOSITORY = "union_repository"
    UNION_UPLOAD = "union_upload"


# END EdgeAttributes


class PlatformUtils:
    @staticmethod
    def commit_model_to_repository(
        model,
        projectName,
        projectOwner,
        branchName,
        userid,
        fmt,
        parserName,
        modelId="TRUNK",
        description="",
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Commit a model to the Models4Insight model repository.

        :returns: A ModelCommit instance describing the commit operation. Note
            that the commit happens asynchronously on the server side. You can
            monitor the progress via query_model requests.
        :rtype: ModelCommit

        :param File model: The model you wish to commit.
        :param str projectName: The name of the project to which you want to
            commit the model.
        :param str projectOwner: The username of the user who owns the project
            you are committing your model to.
        :param str branchName: The name of the branch to which you want to
            commit the model.
        :param str userid: The id of the user committing the model.
        :param str description: Describe the purpose of your commit.

        :exception TypeError: Thrown when any of the parameters (excluding
            module) is not defined or when the query result could not be parsed
            into a ModelCommit instance.
        :exception ValueError: Thrown when any of the parameters is not valid
            or when the query result could otherwise not be parsed.
        :exception requests.exceptions.HTTPError: Thrown when the request
            returned with a 400/500 code variant.
        """

        result = PlatformApi.commit_model(
            branchName,
            M4IUtils.construct_model_id(projectOwner, projectName),
            userid,
            description,
            modelId,
            model,
            contentType=fmt,
            parserName=parserName,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        return result

    # END commit_model_to_repository

    @staticmethod
    def retrieve_model_provenance(
        project_owner=None,
        project_name=None,
        full_project_name=None,
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Retrieve a list of historic events for the given project.

        :returns: A list of historic project events.
        :rtype: list of ModelProvenance

        :param str project_owner: *Optional*. The username of the owner of the
            project. You need to supply either this and the project name, or the
            full project name. Defaults to None.
        :param str project_name: *Optional*. The name of the project. You need
            to supply either this and the project owner, or the full project
            name. Defaults to None.
        :param str full_project_name: *Optional*. The fully qualified name of
            the project as can be retrieved from the repository. You need to
            supply either this, or the project owner and the project name.
            Defaults to None.
        """

        if full_project_name is None:
            if project_owner is None or project_name is None:
                raise ValueError(
                    "Either full_project_name or both project_owner and project_name must be provided"
                )
            full_project_name = M4IUtils.construct_model_id(project_owner, project_name)

        return PlatformApi.model_provenance(
            full_project_name,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

    # END retrieve_model_provenance

    @staticmethod
    def upload_model_data(
        projectOwner=None,
        projectName=None,
        fullProjectName=None,
        branchName="MASTER",
        modelId="TRUNK",
        conceptData=None,
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Upload concept attributes as key-value pairs to the repository. Note
        that, if a property already exists under the same key, the value of
        that property will be overriden.

        :returns: Whether or not the commit operation was successful
        :rtype: bool

        :param str project_owner: *Optional*. The username of the owner of the
            project. You need to supply either this and the project name, or the
            full project name. Defaults to None.
        :param str project_name: *Optional*. The name of the project. You need
            to supply either this and the project owner, or the full project
            name. Defaults to None.
        :param str full_project_name: *Optional*. The fully qualified name of
            the project as can be retrieved from the repository. You need to
            supply either this, or the project owner and the project name.
            Defaults to None.
        :param str branch_id: *Optional*. The name of the branch to which these
            properties belong. Defaults to 'MASTER'.
        :param str model_id: *Optional*. The id of the model you wish to attach
            the properties to. Default is 'TRUNK'.
        :param list concept_data: *Optional*. A list of dictionaries representing
            the properties that should be added to concepts in the model. Each dict
            is structured like this:

            {
                'id': concept id
                'data': {
                     key: value,
                     key: value
                }
            }
        """

        if conceptData is None:
            conceptData = []
        if fullProjectName is None:
            if projectOwner is None or projectName is None:
                raise ValueError(
                    "Either fullProjectName or both projectOwner and projectName must be provided"
                )
            fullProjectName = M4IUtils.construct_model_id(projectOwner, projectName)

        return (
            PlatformApi.data_upload(
                fullProjectName,
                branchName,
                modelId,
                conceptData,
                username=username,
                password=password,
                totp=totp,
                access_token=access_token,
            )
            == "success!"
        )

    # END upload_model_data

    @staticmethod
    def retrieve_data(
        projectOwner=None,
        projectName=None,
        fullProjectName=None,
        branchName="MASTER",
        modelId="TRUNK",
        parserName="archimate3",
        username=None,
        password=None,
        totp=None,
        access_token=None,
        **kwargs,
    ):
        """
        Retrieve data associated with concepts in a model from the repository

        :returns: An object containing a list of properties representing the
            data associated with the model
        :rtype: DataRetrieve

        :param str project_owner: *Optional*. The username of the owner of the
            project. You need to supply either this and the project name, or the
            full project name. Defaults to None.
        :param str project_name: *Optional*. The name of the project. You need
            to supply either this and the project owner, or the full project
            name. Defaults to None.
        :param str full_project_name: *Optional*. The fully qualified name of
            the project as can be retrieved from the repository. You need to
            supply either this, or the project owner and the project name.
            Defaults to None.
        :param str branch_id: *Optional*. The name of the branch to which these
            properties belong. Defaults to 'MASTER'.
        :param str model_id: *Optional*. The id of the model you wish to attach
            the properties to. Default is 'TRUNK'.
        :param str parserName: *Optional*. The name of the meta-model of the
            model you wish to retrieve. Currently, the only valid option is
            'archimate3'. Default is 'archimate3'.
        """

        if fullProjectName is None:
            if projectOwner is None or projectName is None:
                raise ValueError(
                    "Either fullProjectName or both projectOwner and projectName must be provided"
                )
            fullProjectName = M4IUtils.construct_model_id(projectOwner, projectName)

        return PlatformApi.data_retrieve(
            fullProjectName,
            branchName,
            modelId,
            parserName,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

    # END retrieve_data

    @staticmethod
    def merge_branches(
        projectOwner=None,
        projectName=None,
        fullProjectName=None,
        fromBranchName="MASTER",
        toBranchName="MASTER",
        userid=None,
        description="",
        parserName="archimate3",
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Merge two model branches in the repository

        :param str projectOwner: *Optional*. The username of the owner of the
            project. You need to supply either this and the project name, or the
            full project name. Defaults to None.
        :param str fromBranchName: *Optional*. The name of the branch that is
            the source of the merge. Defaults to 'MASTER'.
        :param str toBranchName: *Optional*. The name of the branch that is the
            target of the merge. Defaults to 'MASTER'.
        :param str userid: *Optional*. The id of the user merging the models.
            Defaults to None.
        :param str description: *Optional*. Describe the purpose of the merge.
            Defaults to ''.
        :param str parserName: *Optional*. The name of the meta-model of the
            branches you wish to merge. Currently, the only valid option is
            'archimate3'. Default is 'archimate3'
        :return: ModelCommit
        """

        if fullProjectName is None:
            if projectOwner is None or projectName is None:
                raise ValueError(
                    "Either fullProjectName or both projectOwner and projectName must be provided"
                )
            fullProjectName = M4IUtils.construct_model_id(projectOwner, projectName)

        return PlatformApi.commit_branch(
            description or "",
            fromBranchName,
            fullProjectName,
            toBranchName,
            userid or "",
            parserName=parserName,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

    # END merge_branches

    @staticmethod
    def clone_branch(
        projectOwner=None,
        projectName=None,
        fullProjectName=None,
        fromBranchName="MASTER",
        toBranchName="MASTER",
        userid=None,
        description="",
        parserName="archimate3",
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        """
        Clone a model of one branch to a new branch in the repository

        :param str projectOwner: *Optional*. The username of the owner of the
            project. You need to supply either this and the project name, or the
            full project name. Defaults to None.
        :param str fromBranchName: *Optional*. The name of the branch that is
            the source of the merge. Defaults to 'MASTER'.
        :param str toBranchName: *Optional*. The name of the branch that is the
            target of the merge. Defaults to 'MASTER'.
        :param str userid: *Optional*. The id of the user merging the models.
            Defaults to None.
        :param str description: *Optional*. Describe the purpose of the merge.
            Defaults to ''.
        :param str parserName: *Optional*. The name of the meta-model of the
            branches you wish to merge. Currently, the only valid option is
            'archimate3'. Default is 'archimate3'
        :return: ModelCommit
        """

        if fullProjectName is None:
            if projectOwner is None or projectName is None:
                raise ValueError(
                    "Either fullProjectName or both projectOwner and projectName must be provided"
                )
            fullProjectName = M4IUtils.construct_model_id(projectOwner, projectName)

        return PlatformApi.clone_branch(
            description,
            fullProjectName,
            toBranchName,
            userid or "",
            fromBranchName,
            parserName=parserName,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

    # END clone_branch

    @staticmethod
    def merge_branch_resolve_conflict(
        fromBranch,
        toBranch,
        userid,
        projectOwner,
        projectName,
        description,
        first=False,
        conflict_resolution_template="upload_only",
        model_query_interval=1,
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        merge_branch_name = toBranch
        res = PlatformUtils.merge_branches(
            fromBranchName=fromBranch,
            toBranchName=merge_branch_name,
            userid=userid,
            description=description,
            projectOwner=projectOwner,
            projectName=projectName,
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )
        # self.logger.debug('Merge operation task id: %s' % res.taskId)
        # end of else
        ii = 0
        resq = None
        while (
            resq is None
            or resq["state"]
            not in [
                ModelQueryStateEnum.COMPLETED.value,
                ModelQueryStateEnum.FAILURE.value,
            ]
        ) and ii < 10:
            if ii > 0:
                time.sleep(model_query_interval)
            resq = PlatformApi.query_model(
                res.projectName,
                res.taskId,
                username=username,
                password=password,
                totp=totp,
                access_token=access_token,
            )

            ii = ii + 1
        # END LOOP

        assert resq is not None, "Query result should not be None after polling loop"
        if resq["state"] == ModelQueryStateEnum.FAILURE:
            raise Exception("Merge: Query state failure!")
        else:  # state is completed!
            if (
                "difResult" in resq
                and "state" in resq["difResult"]
                and resq["difResult"]["state"] == ModelQueryDifResultStateEnum.CONFLICT.value
            ):
                resf = PlatformApi.force_commit(
                    addListLeft=[],
                    addListRight=[],
                    description=description,
                    deleteListLeft=[],
                    deleteListRight=[],
                    fromBranch=fromBranch,
                    fromModelId="TRUNK",
                    projectName=res.projectName,
                    taskid=res.taskId,
                    toBranch=merge_branch_name,
                    toModelId="TRUNK",
                    userid=userid,
                    template=conflict_resolution_template,
                    username=username,
                    password=password,
                    totp=totp,
                    access_token=access_token,
                )

                resfq = None
                jj = 0
                while (
                    resfq is None
                    or resfq["state"]
                    not in [
                        ModelQueryStateEnum.COMPLETED.value,
                        ModelQueryStateEnum.FAILURE.value,
                    ]
                ) and jj < 10:
                    if jj > 0:
                        time.sleep(model_query_interval)
                    resfq = PlatformApi.query_model(
                        resf.projectName,
                        resf.taskId,
                        username=username,
                        password=password,
                        totp=totp,
                        access_token=access_token,
                    )

                    jj = jj + 1
                assert resfq is not None, "Force commit query result should not be None after polling loop"
                if resfq["state"] == ModelQueryStateEnum.FAILURE:
                    raise Exception("Merge force: Query state failure!")
                else:  # state is completed!
                    if resfq.get("difResult", {}).get("state") == ModelQueryDifResultStateEnum.CONFLICT.value:
                        raise Exception("Merge force: Query state failure!")
                    else:
                        # model committed!
                        ret = True
            else:
                # model committed!
                ret = True
        return ret

    # END merge_branch_resolve_conflict

    @staticmethod
    def commit_to_repository_resolve_conflict(
        model=None,
        branch=None,
        userid=None,
        projectOwner=None,
        projectName=None,
        description=None,
        parserName=None,
        model_query_interval=1,
        conflict_resolution_template="upload_only",
        username=None,
        password=None,
        totp=None,
        access_token=None,
    ):
        res = PlatformUtils.commit_model_to_repository(
            model,
            branchName=branch or "",
            userid=userid or "",
            description=description or "",
            projectOwner=projectOwner,
            projectName=projectName,
            fmt="json",
            parserName="archimate3",
            username=username,
            password=password,
            totp=totp,
            access_token=access_token,
        )

        ii = 0
        resq = None
        while (
            resq is None
            or resq["state"]
            not in [
                ModelQueryStateEnum.COMPLETED.value,
                ModelQueryStateEnum.FAILURE.value,
            ]
        ) and ii < 10:
            if ii > 0:
                time.sleep(model_query_interval)
            resq = PlatformApi.query_model(
                res.projectName,
                res.taskId,
                username=username,
                password=password,
                totp=totp,
                access_token=access_token,
            )

            ii = ii + 1
        assert resq is not None, "Query result should not be None after polling loop"
        if resq["state"] == ModelQueryStateEnum.FAILURE.value:
            raise Exception("Commit: Query state failure!")
        else:  # state is completed!
            if (
                "difResult" in resq
                and "state" in resq["difResult"]
                and resq["difResult"]["state"] == ModelQueryDifResultStateEnum.CONFLICT.value
            ):
                # resolve conflict
                resf = PlatformApi.force_commit(
                    addListLeft=[],
                    addListRight=[],
                    description=description or "",
                    deleteListLeft=[],
                    deleteListRight=[],
                    fromBranch=branch or "",
                    fromModelId=res.taskId,
                    projectName=res.projectName,
                    taskid=res.taskId,
                    toBranch=branch or "",
                    toModelId="TRUNK",
                    userid=userid or "",
                    template=conflict_resolution_template,
                    username=username,
                    password=password,
                    totp=totp,
                    access_token=access_token,
                )
                resfq = None
                jj = 0
                while (
                    resfq is None
                    or resfq["state"]
                    not in [
                        ModelQueryStateEnum.COMPLETED.value,
                        ModelQueryStateEnum.FAILURE.value,
                    ]
                ) and jj < 10:
                    if jj > 0:
                        time.sleep(model_query_interval)
                    resfq = PlatformApi.query_model(
                        resf.projectName,
                        resf.taskId,
                        username=username,
                        password=password,
                        totp=totp,
                        access_token=access_token,
                    )
                    jj = jj + 1
                assert resfq is not None, "Force commit query result should not be None after polling loop"
                if resfq["state"] == ModelQueryStateEnum.FAILURE:
                    raise Exception("Commit force: Query state failure!")
                else:  # state is completed!
                    if resfq.get("difResult", {}).get("state") == ModelQueryDifResultStateEnum.CONFLICT.value:
                        raise Exception("Commit force: Query state failure!")
                    else:
                        # model committed!
                        ret = True
            else:
                # model committed!
                ret = True

        return ret


# END commit_to_repository_resolve_conflict

# END PlatformUtils
