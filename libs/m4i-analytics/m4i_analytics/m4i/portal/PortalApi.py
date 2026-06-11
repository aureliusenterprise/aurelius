import numbers

import m4i_analytics.m4i.portal.config as config
from m4i_analytics.m4i.ApiUtils import ApiUtils, ContentType
from m4i_analytics.m4i.portal.model.CreateProjectResponse import CreateProjectResponse
from m4i_analytics.m4i.portal.model.TableDashboardResponse import TableDashboardResponse


class PortalApi:
    """
    This class implements various API calls to functions provided by the M4I portal
    """

    @staticmethod
    def instanceworkflow_query(taskid, projectid, run_by, instanceid):
        if taskid is None:
            raise TypeError("Taskid is not defined")
        elif not isinstance(taskid, str):
            raise ValueError("Taskid should be a string")
        elif projectid is None:
            raise TypeError("Projectid is not defined")
        elif not isinstance(projectid, str):
            raise ValueError("Projectid should be a string")
        elif instanceid is None:
            raise TypeError("Instanceid is not defined")
        elif not isinstance(instanceid, int):
            raise ValueError("Instanceid should be a number")

        result = ApiUtils.get(
            config.INSTANCEWORKFLOW_QUERY_ENDPOINT,
            content_type=ContentType.JSON,
            params={
                config.TASK_ID_KEY: taskid,
                config.PROJECT_NAME_KEY: projectid,
                config.RUN_BY_KEY: run_by,
                config.INSTANCEID_KEY: instanceid,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
        )

        return result

    @staticmethod
    def create_project(
        taskid, projectid, run_by, owner_username, owner_email, owner_firstname="John", owner_lastname="Doe"
    ):
        """
        Create a new project on the portal.
        A project comes with a modelview dashboard by default.

        :returns: The ID of the created dashboard
        :rtype: CreateProjectResponse

        :param str taskid: A unique identifier for the task instance you are starting.
        :param str projectid: A unique name for the project.
        :param str run_by: A unique identifier for the user who started the operation.
        :param str owner_username: The username of the user who will own the project
        :param str owner_email: The email of the user who will own the project.
        :param str owner_firstname: *Optional*. The first name of the user who will own
        the project. By default, is set to 'John'.
        :param str owner_lastname: *Optional*. The last name of the user who will own
        the project. By default, is set to 'Doe'.

        :exception TypeError: Thrown when any of the parameters (excluding
        owner_firstname and owner_lastname) is not defined.
        :exception ValueError: Thrown when any of the parameters is not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if taskid is None:
            raise TypeError("Taskid is not defined")
        elif not isinstance(taskid, str):
            raise ValueError("Taskid should be a string")
        elif projectid is None:
            raise TypeError("Projectid is not defined")
        elif not isinstance(projectid, str):
            raise ValueError("Projectid should be a string")
        elif run_by is None:
            raise TypeError("Run_by is not defined")
        elif not isinstance(run_by, str):
            raise ValueError("Run_by should be a string")
        elif owner_username is None:
            raise TypeError("Owner_username is not defined")
        elif not isinstance(owner_username, str):
            raise ValueError("Owner_username should be a string")
        elif owner_email is None:
            raise TypeError("Owner_email is not defined")
        elif not isinstance(owner_email, str):
            raise ValueError("Owner_email should be a string")
        elif owner_firstname is not None and not isinstance(owner_firstname, str):
            raise ValueError("Owner_firstname should be a string")
        elif owner_lastname is not None and not isinstance(owner_lastname, str):
            raise ValueError("Owner_lastname should be a string")

        result = ApiUtils.get(
            config.CREATE_PROJECT_ENDPOINT,
            content_type=ContentType.JSON,
            params={
                config.TASK_ID_KEY: taskid,
                config.PROJECT_NAME_KEY: projectid,
                config.RUN_BY_KEY: run_by,
                config.USERNAME_KEY: owner_username,
                config.EMAIL_KEY: owner_email,
                config.FIRST_NAME_KEY: owner_firstname,
                config.LAST_NAME_KEY: owner_lastname,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
        )

        assert isinstance(result, dict), f"Expected dict for create_project, got {type(result)}"
        return CreateProjectResponse(**result)

    # END create_project

    @staticmethod
    def update_project(
        taskid, projectid, run_by, branch_name, model_timestamp, data_timestamp, parser_name="archimate3"
    ):
        """
        Update the model and data associated with a project in a single call.

        :returns: A string signaling that the operation completed successfully ('OK')
        :rtype: str

        :param str taskid: A unique identifier for the task instance you are starting.
        :param str projectid: The unique name of the project you wish to update.
        :param str run_by: A unique identifier for the user who started the operation.
        :param str branch_name: The name of the branch of the model you wish to use as
        the source of the update.
        :param int model_timestamp: The version of the model you wish to use as the
        source of the update.
        :param int data_timestamp: The version of the data you wish to use as the source
        of the update.
        :param str parser_name: *Optional*. The name of the meta-model of the model you
        wish to use as the source of the update. Currently, the only valid option is
        'archimate3'. Defaults to 'archimate3'.

        :exception TypeError: Thrown when any of the parameters is not defined.
        :exception ValueError: Thrown when any of the parameters is not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if taskid is None:
            raise TypeError("Taskid is not defined")
        elif not isinstance(taskid, str):
            raise ValueError("Taskid should be a string")
        elif projectid is None:
            raise TypeError("Projectid is not defined")
        elif not isinstance(projectid, str):
            raise ValueError("Projectid should be a string")
        elif run_by is None:
            raise TypeError("Run_by is not defined")
        elif not isinstance(run_by, str):
            raise ValueError("Run_by should be a string")
        elif branch_name is None:
            raise TypeError("Branch_name is not defined")
        elif not isinstance(branch_name, str):
            raise ValueError("Branch_name should be a string")
        elif model_timestamp is None:
            raise TypeError("Model_timestamp is not defined")
        elif not isinstance(model_timestamp, numbers.Integral):
            raise ValueError("Model_timestamp should be an int")
        elif data_timestamp is None:
            raise TypeError("Data_timestamp is not defined")
        elif not isinstance(data_timestamp, numbers.Integral):
            raise ValueError("Data_timestamp should be an int")
        elif parser_name is None:
            raise TypeError("Parser_name is not defined")
        elif not isinstance(parser_name, str):
            raise ValueError("Parser_name should be a string")

        result = ApiUtils.get(
            config.UPDATE_PROJECT_ENDPOINT,
            content_type=ContentType.TEXT,
            params={
                config.TASK_ID_KEY: taskid,
                config.PROJECT_NAME_KEY: projectid,
                config.RUN_BY_KEY: run_by,
                config.BRANCH_NAME_KEY: branch_name,
                config.DELTA_REVISION_KEY: model_timestamp,
                config.DATA_REVISION_KEY: data_timestamp,
                config.PARSER_NAME_KEY: parser_name,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
        )

        return result

    # END update_project

    @staticmethod
    def update_project_model(taskid, projectid, run_by, branch_name, version, parser_name="archimate3"):
        """
        Update the model associated with a project.

        :returns: A string signaling that the operation completed successfully ('OK')
        :rtype: str

        :param str taskid: A unique identifier for the task instance you are starting.
        :param str projectid: The unique name of the project you wish to update.
        :param str run_by: A unique identifier for the user who started the operation.
        :param str branch_name: The name of the branch of the model you wish to use as
        the source of the update.
        :param int version: The version of the model you wish to use as the source of
        the update.
        :param str parser_name: *Optional*. The name of the meta-model of the model you
        wish to use as the source of the update. Currently, the only valid option is
        'archimate3'. Defaults to 'archimate3'.

        :exception TypeError: Thrown when any of the parameters is not defined.
        :exception ValueError: Thrown when any of the parameters is not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if taskid is None:
            raise TypeError("Taskid is not defined")
        elif not isinstance(taskid, str):
            raise ValueError("Taskid should be a string")
        elif projectid is None:
            raise TypeError("Projectid is not defined")
        elif not isinstance(projectid, str):
            raise ValueError("Projectid should be a string")
        elif run_by is None:
            raise TypeError("Run_by is not defined")
        elif not isinstance(run_by, str):
            raise ValueError("Run_by should be a string")
        elif branch_name is None:
            raise TypeError("Branch_name is not defined")
        elif not isinstance(branch_name, str):
            raise ValueError("Branch_name should be a string")
        elif version is None:
            raise TypeError("Version is not defined")
        elif not isinstance(version, numbers.Integral):
            raise ValueError("Version should be an int")
        elif parser_name is None:
            raise TypeError("Parser_name is not defined")
        elif not isinstance(parser_name, str):
            raise ValueError("Parser_name should be a string")

        result = ApiUtils.get(
            config.DELTA_ENDPOINT,
            content_type=ContentType.TEXT,
            params={
                config.TASK_ID_KEY: taskid,
                config.PROJECT_NAME_KEY: projectid,
                config.RUN_BY_KEY: run_by,
                config.BRANCH_NAME_KEY: branch_name,
                config.VERSION_KEY: version,
                config.PARSER_NAME_KEY: parser_name,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
        )

        return result

    # END update_project_model

    @staticmethod
    def update_project_model_async(taskid, projectid, run_by, branch_name, version, parser_name="archimate3"):
        """
        Update the model associated with a project via the async function.

        :returns: A string signaling that the operation completed successfully ('OK')
        :rtype: str

        :param str taskid: A unique identifier for the task instance you are starting.
        :param str projectid: The unique name of the project you wish to update.
        :param str run_by: A unique identifier for the user who started the operation.
        :param str branch_name: The name of the branch of the model you wish to use as
        the source of the update.
        :param int version: The version of the model you wish to use as the source of
        the update.
        :param str parser_name: *Optional*. The name of the meta-model of the model you
        wish to use as the source of the update. Currently, the only valid option is
        'archimate3'. Defaults to 'archimate3'.

        :exception TypeError: Thrown when any of the parameters is not defined.
        :exception ValueError: Thrown when any of the parameters is not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if taskid is None:
            raise TypeError("Taskid is not defined")
        elif not isinstance(taskid, str):
            raise ValueError("Taskid should be a string")
        elif projectid is None:
            raise TypeError("Projectid is not defined")
        elif not isinstance(projectid, str):
            raise ValueError("Projectid should be a string")
        elif run_by is None:
            raise TypeError("Run_by is not defined")
        elif not isinstance(run_by, str):
            raise ValueError("Run_by should be a string")
        elif branch_name is None:
            raise TypeError("Branch_name is not defined")
        elif not isinstance(branch_name, str):
            raise ValueError("Branch_name should be a string")
        elif version is None:
            raise TypeError("Version is not defined")
        elif not isinstance(version, numbers.Integral):
            raise ValueError("Version should be an int")
        elif parser_name is None:
            raise TypeError("Parser_name is not defined")
        elif not isinstance(parser_name, str):
            raise ValueError("Parser_name should be a string")

        result = ApiUtils.get(
            config.DELTA_ASYNC_ENDPOINT,
            content_type=ContentType.JSON,
            params={
                config.TASK_ID_KEY: taskid,
                config.PROJECT_NAME_KEY: projectid,
                config.RUN_BY_KEY: run_by,
                config.BRANCH_NAME_KEY: branch_name,
                config.VERSION_KEY: version,
                config.PARSER_NAME_KEY: parser_name,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
        )

        return result

    # END update_project_model

    @staticmethod
    def update_project_data(taskid, projectid, run_by, branch_name, version, parser_name="archimate3"):
        """
        Update the data associated with a project.

        :returns: A string signaling that the operation completed successfully ('OK')
        :rtype: str

        :param str taskid: A unique identifier for the task instance you are starting.
        :param str projectid: The unique name of the project you wish to update.
        :param str run_by: A unique identifier for the user who started the operation.
        :param str branch_name: The name of the branch of the model you wish to use as
        the source of the update.
        :param int version: The version of the data you wish to use as the source of the
        update.
        :param str parser_name: *Optional*. The name of the meta-model of the model you
        wish to use as the source of the update. Currently, the only valid option is
        'archimate3'. Defaults to 'archimate3'.

        :exception TypeError: Thrown when any of the parameters is not defined.
        :exception ValueError: Thrown when any of the parameters is not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if taskid is None:
            raise TypeError("Taskid is not defined")
        elif not isinstance(taskid, str):
            raise ValueError("Taskid should be a string")
        elif projectid is None:
            raise TypeError("Projectid is not defined")
        elif not isinstance(projectid, str):
            raise ValueError("Projectid should be a string")
        elif run_by is None:
            raise TypeError("Run_by is not defined")
        elif not isinstance(run_by, str):
            raise ValueError("Run_by should be a string")
        elif branch_name is None:
            raise TypeError("Branch_name is not defined")
        elif not isinstance(branch_name, str):
            raise ValueError("Branch_name should be a string")
        elif version is None:
            raise TypeError("Version is not defined")
        elif not isinstance(version, numbers.Integral):
            raise ValueError("Version should be an int")
        elif parser_name is None:
            raise TypeError("Parser_name is not defined")
        elif not isinstance(parser_name, str):
            raise ValueError("Parser_name should be a string")

        result = ApiUtils.get(
            config.DATA_ENDPOINT,
            content_type=ContentType.TEXT,
            params={
                config.TASK_ID_KEY: taskid,
                config.PROJECT_NAME_KEY: projectid,
                config.RUN_BY_KEY: run_by,
                config.BRANCH_NAME_KEY: branch_name,
                config.VERSION_KEY: version,
                config.PARSER_NAME_KEY: parser_name,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
        )

        return result

    # END update_project_data

    @staticmethod
    def create_table_dashboard(taskid, projectid, run_by, tablename):
        """
        Create a dashboard with a table mirroring a table in the database,
        based on the given tablename

        :returns: The ID of the created dashboard
        :rtype: TableDashboardResponse or str

        :param str taskid: A unique identifier for the task instance you are starting.
        :param str projectid: The unique name of the project you wish to update.
        :param str run_by: A unique identifier for the user who started the operation.
        :param str tablename: The name of the table in the database you wish to mirror
        on the dashboard

        :exception TypeError: Thrown when any of the parameters is not defined.
        :exception ValueError: Thrown when any of the parameters is not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if taskid is None:
            raise TypeError("Taskid is not defined")
        elif not isinstance(taskid, str):
            raise ValueError("Taskid should be a string")
        elif projectid is None:
            raise TypeError("Projectid is not defined")
        elif not isinstance(projectid, str):
            raise ValueError("Projectid should be a string")
        elif run_by is None:
            raise TypeError("Run_by is not defined")
        elif not isinstance(run_by, str):
            raise ValueError("Run_by should be a string")
        elif tablename is None:
            raise TypeError("Tablename is not defined")
        elif not isinstance(tablename, str):
            raise ValueError("Tablename should be a string")

        response = ApiUtils.get(
            config.TABLE_DASHBOARD_ENDPOINT,
            content_type=ContentType.JSON,
            params={
                config.TASK_ID_KEY: taskid,
                config.PROJECT_NAME_KEY: projectid,
                config.RUN_BY_KEY: run_by,
                config.TABLENAME_KEY: tablename,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
        )

        result = response

        if not isinstance(response, str):
            result = TableDashboardResponse(**result)

        return result

    # END create_table_dashboard

    @staticmethod
    def add_project_users(taskid, projectid, run_by, users):
        """
        Give one or more users access to a project

        :returns: The ID of the role assigned to the users
        :rtype: int

        :param str taskid: A unique identifier for the task instance you are starting.
        :param str projectid: The unique name of the project you wish to update.
        :param str run_by: A unique identifier for the user who started the operation.
        :param list users: A list of the users you wish to give access to the project

        :exception TypeError: Thrown when any of the parameters is not defined.
        :exception ValueError: Thrown when any of the parameters is not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if taskid is None:
            raise TypeError("Taskid is not defined")
        elif not isinstance(taskid, str):
            raise ValueError("Taskid should be a string")
        elif projectid is None:
            raise TypeError("Projectid is not defined")
        elif not isinstance(projectid, str):
            raise ValueError("Projectid should be a string")
        elif run_by is None:
            raise TypeError("Run_by is not defined")
        elif not isinstance(run_by, str):
            raise ValueError("Run_by should be a string")
        elif users is None:
            raise TypeError("Users is not defined")
        elif not isinstance(users, list):
            raise ValueError("Users should be a list")
        elif len(users) == 0:
            raise ValueError("Users should not be empty")

        result = ApiUtils.get(
            config.DELTA_ENDPOINT,
            content_type=ContentType.TEXT,
            params={
                config.TASK_ID_KEY: taskid,
                config.PROJECT_NAME_KEY: projectid,
                config.RUN_BY_KEY: run_by,
                config.USERS_KEY: users,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
        )

        return result

    # END add_project_users

    @staticmethod
    def remove_project_user(taskid, projectid, run_by, username):
        """
        Remove access to a project for a particular user

        :returns: A string signaling that the operation completed successfully ('OK')
        :rtype: str

        :param str taskid: A unique identifier for the task instance you are starting.
        :param str projectid: The unique name of the project you wish to update.
        :param str run_by: A unique identifier for the user who started the operation.
        :param str username: The username of the user for whom you wish to revoke access

        :exception TypeError: Thrown when any of the parameters is not defined.
        :exception ValueError: Thrown when any of the parameters is not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if taskid is None:
            raise TypeError("Taskid is not defined")
        elif not isinstance(taskid, str):
            raise ValueError("Taskid should be a string")
        elif projectid is None:
            raise TypeError("Projectid is not defined")
        elif not isinstance(projectid, str):
            raise ValueError("Projectid should be a string")
        elif run_by is None:
            raise TypeError("Run_by is not defined")
        elif not isinstance(run_by, str):
            raise ValueError("Run_by should be a string")
        elif username is None:
            raise TypeError("Username is not defined")
        elif not isinstance(username, str):
            raise ValueError("Username should be a string")

        result = ApiUtils.get(
            config.DELTA_ENDPOINT,
            content_type=ContentType.TEXT,
            params={
                config.TASK_ID_KEY: taskid,
                config.PROJECT_NAME_KEY: projectid,
                config.RUN_BY_KEY: run_by,
                config.RM_USER_USERNAME_KEY: username,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
        )

        return result

    # END remove_project_user

    @staticmethod
    def unpublish_project(taskid, projectid, run_by):
        """
        Remove access to a project for all current members

        :returns: A string signaling that the operation completed successfully ('OK')
        :rtype: str

        :param str taskid: A unique identifier for the task instance you are starting.
        :param str projectid: The unique name of the project you wish to update.
        :param str run_by: A unique identifier for the user who started the operation.

        :exception TypeError: Thrown when any of the parameters is not defined.
        :exception ValueError: Thrown when any of the parameters is not valid.
        :exception requests.exceptions.HTTPError: Thrown when the request returned with
        a 400/500 code variant.
        """

        if taskid is None:
            raise TypeError("Taskid is not defined")
        elif not isinstance(taskid, str):
            raise ValueError("Taskid should be a string")
        elif projectid is None:
            raise TypeError("Projectid is not defined")
        elif not isinstance(projectid, str):
            raise ValueError("Projectid should be a string")
        elif run_by is None:
            raise TypeError("Run_by is not defined")
        elif not isinstance(run_by, str):
            raise ValueError("Run_by should be a string")

        result = ApiUtils.get(
            config.DELTA_ENDPOINT,
            content_type=ContentType.TEXT,
            params={
                config.TASK_ID_KEY: taskid,
                config.PROJECT_NAME_KEY: projectid,
                config.RUN_BY_KEY: run_by,
            },
            proxies=config.PROXIES,
            use_default_proxies=config.USE_DEFAULT_PROXIES,
        )

        return result

    # END unpublish_project


# END PortalApi
