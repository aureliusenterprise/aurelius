class M4IUtils:
    @staticmethod
    def construct_model_id(project_owner: str, project_name: str) -> str:
        """
        Returns a string formatted as a model ID based on the given
        project owner and project name

        :returns: A model id string
        :rtype: str

        :param str project_owner: The name of the owner of the project.
        :param str project_name: The name of the project.
        """

        if not project_owner:
            raise ValueError("Project owner should be defined!")
        elif not project_name:
            raise ValueError("Project name should be defined!")

        return f"{project_owner}__{project_name}".replace(" ", "_")

    # END construct_model_id
