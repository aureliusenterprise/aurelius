import json
import logging
import time

from m4i_analytics.graphs.languages.archimate.ArchimateUtils import ArchimateUtils
from m4i_analytics.m4i.ApiUtils import ApiUtils
from m4i_analytics.m4i.platform.model.ModelQuery import StateEnum as ModelQueryStateEnum
from m4i_analytics.m4i.platform.model.ModelQueryDifResult import (
    StateEnum as ModelQueryDifResultStateEnum,
)
from m4i_analytics.m4i.platform.PlatformApi import PlatformApi
from m4i_analytics.m4i.platform.PlatformUtils import PlatformUtils
from m4i_analytics.m4i.portal.PortalApi import PortalApi
from m4i_analytics.monitoring.propagation import propagate


class Monitoring:
    merge_branch_name = "all"
    userid = "monitoring"
    extractors = []
    model_options = {}
    portal_options = {}
    pathing_options = {}
    model_generation_interval = 1
    status_retrieval_interval = 1
    status_retrieval_offset = 1
    model_query_interval = 1
    only_status = False
    logger = logging.getLogger("Monitoring")

    def __init__(
        self,
        extractors,
        model_options,
        portal_options,
        pathing_options,
        merge_branch_name="all",
        userid="monitoring",
        model_generation_interval=1,
        model_generation_offset=1,
        status_retrieval_interval=1,
        status_retrieval_offset=1,
        model_query_interval=1,
        only_status=False,
        log_file_path=None,
        log_file_format="%(asctime)s - %(name)s -%(relativeCreated)6d "
        "%(threadName)s - %(levelname)s - %(message)s",
    ):
        self.merge_branch_name = merge_branch_name
        self.userid = userid
        self.extractors = extractors
        self.model_options = model_options
        self.portal_options = portal_options
        self.pathing_options = pathing_options
        self.model_generation_interval = model_generation_interval
        self.model_generation_offset = model_generation_offset
        self.status_retrieval_interval = status_retrieval_interval
        self.status_retrieval_offset = status_retrieval_offset
        self.model_query_interval = model_query_interval
        self.only_status = only_status
        # Configure the logger
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(log_file_format)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if log_file_path is not None:
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    # END

    """def handle_merge_list(self, branchList, conflict_resolution_template='upload_only'):
        for branch in branchList:
            flag = False
            obs = self.handle_merge(branch['branchName']).subscribe(lambda i: flag=True)
            while not flag:
                pass
            Observable.concat_all([self.handle_merge(b) for b in branchList]).subscribe()
    """

    def handle_merge(self, fromBranch, first=False, conflict_resolution_template="upload_only"):
        ret = False

        # fromBranch = entry['branchName']
        self.logger.debug(f"Merge: process branch: {fromBranch}")
        self.logger.debug(f"Merge: conflict_resolution_template: {str(conflict_resolution_template)}")
        # if first:
        #    res = PlatformUtils.clone_branch(fromBranchName=fromBranch
        #                , toBranchName=self.merge_branch_name
        #                , userid=self.userid
        #                , description='%s model' % fromBranch
        #                , **self.model_options)
        # else:
        res = PlatformUtils.merge_branches(
            fromBranchName=fromBranch,
            toBranchName=self.merge_branch_name,
            userid=self.userid,
            description=f"{fromBranch} model",
            **self.model_options,
        )
        self.logger.debug(f"Merge operation task id: {res.taskId}")
        # end of else
        ii = 0
        resq = None
        while (
            resq is None
            or resq.state
            not in [
                ModelQueryStateEnum.COMPLETED.value,
                ModelQueryStateEnum.FAILURE.value,
            ]
        ) and ii < 10:
            if ii > 0:
                time.sleep(((self.model_query_interval + 0.5) * (ii + 1)) // 1)
            resq = PlatformApi.query_model(res.projectName, res.taskId)
            self.logger.debug(f"Commit: Query state: {resq.state}")
            ii = ii + 1
        assert resq is not None, "Merge query timed out"
        if resq.state == ModelQueryStateEnum.FAILURE:
            self.logger.debug("Merge: Query state: failure!")
            raise Exception("Merge: Query state failure!")
        else:  # state is completed!
            if resq.difResult.state == ModelQueryDifResultStateEnum.CONFLICT.value:
                self.logger.info("Merge Conflict resolution: Replacing old model version")
                resf = PlatformApi.force_commit(
                    addListLeft=[],
                    addListRight=[],
                    description=f"merge repository version with new model version from branch {fromBranch}",
                    deleteListLeft=[],
                    deleteListRight=[],
                    fromBranch=fromBranch,
                    fromModelId="TRUNK",
                    projectName=res.projectName,
                    taskid=res.taskId,
                    toBranch=self.merge_branch_name,
                    toModelId="TRUNK",
                    userid=self.userid,
                    template=conflict_resolution_template,
                )
                self.logger.debug(f"Merge Conflict resolution: Replace operation task id: {resf.taskId}")
                resfq = None
                jj = 0
                while (
                    resfq is None
                    or resfq.state
                    not in [
                        ModelQueryStateEnum.COMPLETED.value,
                        ModelQueryStateEnum.FAILURE.value,
                    ]
                ) and jj < 10:
                    if jj > 0:
                        time.sleep(((self.model_query_interval + 0.5) * (ii + 1)) // 1)
                    resfq = PlatformApi.query_model(resf.projectName, resf.taskId)
                    self.logger.debug(f"Merge force: Query state: {resfq.state}")
                    jj = jj + 1
                assert resfq is not None, f"Merge force query timed out after {jj} attempts"
                if resfq.state == ModelQueryStateEnum.FAILURE:
                    raise Exception("Merge force: Query state failure!")
                else:  # state is completed!
                    if resfq.difResult.state == ModelQueryDifResultStateEnum.CONFLICT.value:
                        self.logger.debug("Merge force: Query state: failure!")
                        raise Exception("Merge force: Query state failure!")
                    else:
                        # model committed!
                        self.logger.debug("Merge force: Query state: model committed!")
                        ret = True
            else:
                # model committed!
                self.logger.debug("Merge: Query state: model committed!")
                ret = True
        return ret

    # END handle_merge

    def handle_commit(self, model, branch, conflict_resolution_template="upload_only"):
        ret = False
        # try:
        res = ArchimateUtils.commit_model_to_repository(
            model["model"],
            branchName=branch,
            userid=self.userid,
            description=f"{branch} model",
            **self.model_options,
        )
        self.logger.debug(f"Commit operation task id: {res.taskId}")
        ii = 0
        resq = None
        while (
            resq is None
            or resq.state
            not in [
                ModelQueryStateEnum.COMPLETED.value,
                ModelQueryStateEnum.FAILURE.value,
            ]
        ) and ii < 10:
            if ii > 0:
                time.sleep(((self.model_query_interval + 0.5) * (ii + 1)) // 1)
            resq = PlatformApi.query_model(res.projectName, res.taskId)
            self.logger.debug(f"Commit: Query state: {resq.state}")
            ii = ii + 1
        assert resq is not None, "Commit query timed out"
        if resq.state == ModelQueryStateEnum.FAILURE:
            self.logger.debug("Commit: Query state: failure!")
            raise Exception("Commit: Query state failure!")
        else:  # state is completed!
            if resq.difResult is None:
                self.logger.debug("Commit: Query state: no result yet!")
                raise Exception("Commit: Query state no result yet!")
            elif resq.difResult.state == ModelQueryDifResultStateEnum.CONFLICT.value:
                # resolve conflict
                self.logger.info("Commit: Replacing old model version")
                resf = PlatformApi.force_commit(
                    addListLeft=[],
                    addListRight=[],
                    description="replacing old model version",
                    deleteListLeft=[],
                    deleteListRight=[],
                    fromBranch=branch,
                    fromModelId=res.taskId,
                    projectName=res.projectName,
                    taskid=res.taskId,
                    toBranch=branch,
                    toModelId="TRUNK",
                    userid=self.userid,
                    template=conflict_resolution_template,
                )
                self.logger.debug(f"Commit: Replace operation task id: {resf.taskId}")
                resfq = None
                jj = 0
                while (
                    resfq is None
                    or resfq.state
                    not in [
                        ModelQueryStateEnum.COMPLETED.value,
                        ModelQueryStateEnum.FAILURE.value,
                    ]
                ) and jj < 10:
                    if jj > 0:
                        time.sleep(((self.model_query_interval + 0.5) * (ii + 1)) // 1)
                    resfq = PlatformApi.query_model(resf.projectName, resf.taskId)
                    self.logger.debug(f"Commit force: Query state: {resfq.state}")
                    jj = jj + 1
                assert resfq is not None, f"Commit force query timed out after {jj} attempts"
                if resfq.state == ModelQueryStateEnum.FAILURE:
                    raise Exception("Commit force: Query state failure!")
                else:  # state is completed!
                    if resfq.difResult.state == ModelQueryDifResultStateEnum.CONFLICT.value:
                        self.logger.debug("Commit force: Query state: failure!")
                        raise Exception("Commit force: Query state failure!")
                    else:
                        # model committed!
                        self.logger.debug("Commit: Query state: model committed!")
                        ret = True
            else:
                # model committed!
                self.logger.debug("Commit: Query state: model committed!")
                ret = True

        # except Exception as e:
        #    self.logger.debug('Exception: %s' % e)
        #    return ret
        return ret

    # END handle_commit

    def monitor(self):
        # if not self.only_status:
        # Create the project on the portal
        # self.logger.info('Creating the project on the portal!')
        # res = PortalApi.create_project(
        #            taskid='monitoring_create_project'
        #            , projectid='{0}__{1}'.format(
        #                    self.model_options['projectOwner']
        #                    , self.model_options['projectName'].replace(' ', '_'))
        #            , run_by='monitoring'
        #            , owner_username=self.model_options['projectOwner']
        #            , owner_email=self.portal_options['project_owner_email'])
        # self.logger.info('Project created!')
        # else:
        #    self.logger.info('Skip creating the project on the portal!')

        def do_extract(extractor, data_only=False):
            try:
                return extractor.extract(data_only)
            except Exception as exc:
                self.logger.exception(f"do_extract: exception in extract() {str(exc)}")
                return None

        def do_run(data_only=False):
            # Model Extraction
            ret = None
            branches = []
            self.logger.debug("Start model generation!")
            if data_only:
                self.logger.debug("Only generate State information")
            for ex in self.extractors:
                self.logger.info(f"Start generating the {ex.branch_name} model!")
                x = do_extract(ex, data_only)
                # self.logger.info('Finished generating the %s model!' % x['branchName'])
                # commit the model
                if x is None:
                    self.logger.info("Failed generating the model!")
                    raise Exception("Failed generating the model!")
                else:
                    if not data_only:
                        # ready to do commit
                        self.logger.info("Start committing the {} model!".format(x["branchName"]))
                        y = self.handle_commit(x, x["branchName"])
                        self.logger.info("Finished committing the {} model!".format(x["branchName"]))
                        self.logger.info(f"Commit was successful: {str(y)}")
                        ret = y
                    # commiting data
                    self.logger.info("Start uploading the {} data!".format(x["branchName"]))
                    PlatformUtils.upload_model_data(
                        branchName=x["branchName"],
                        conceptData=x["data"],
                        **self.model_options,
                    )
                    self.logger.info("Finished uploading the {} data!".format(x["branchName"]))
                    branches.append(x["branchName"])
            # END for ex
            # merge branches
            ii = 0
            for branch in branches:
                self.logger.info(f"Start merging the {ii}th model with the {self.merge_branch_name} model!")
                if ii == 0 and not self.only_status:
                    x = self.handle_merge(branch, True, "upload_only")
                else:
                    x = self.handle_merge(branch, False, "union_upload")
                self.logger.info(
                    f"Finished merging the {ii}th model with the {self.merge_branch_name} model!"
                )
                self.logger.info(f"Merge was successful: {str(x)}")
                if x:
                    ii = ii + 1
            # END for branch
            merge_success = ii > 0
            self.logger.info("Finished merging the models!")

            if merge_success:
                # propagate state
                self.logger.info(
                    f"Start propagating statuses for the integrated model in branch {self.merge_branch_name}!"
                )
                resp = {
                    "branchName": self.merge_branch_name,
                    "propagation": propagate(
                        {
                            "projectOwner": self.model_options["projectOwner"],
                            "projectName": self.model_options["projectName"],
                            "branchName": self.merge_branch_name,
                        }
                    ),
                }
                self.logger.info(
                    f"Finished propagating statuses for integrated model in branch {resp['branchName']}!"
                )
                self.logger.info("Start uploading the {} propagation data!".format(resp["branchName"]))
                PlatformUtils.upload_model_data(
                    branchName=resp["branchName"],
                    conceptData=resp["propagation"],
                    **self.model_options,
                )
                self.logger.info("Finished uploading the {} propagation data!".format(resp["branchName"]))

                # start pathing
                self.logger.info("Start processing paths in the model!")
                params = {
                    "project_name": "{}__{}".format(
                        self.model_options["projectOwner"],
                        self.model_options["projectName"],
                    ),
                    "branch_name": self.pathing_options["model_options"]["branchName"],
                    "pathing_target_table": self.pathing_options["pathing_target_table"],
                    "timeseries_target_table": self.pathing_options["timeseries_target_table"],
                    "allowed_relations": json.dumps(
                        [rel["shorthand"] for rel in self.pathing_options["allowed_relationship_types"]]
                    ),
                }

                result = ApiUtils.get("http://portal.models4insight.com/m4i/rest/pathing", params)
                self.logger.info(
                    "URL send to the portal {}{}".format(
                        "http://portal.models4insight.com/m4i/rest/pathing", params
                    )
                )
                self.logger.info(f"URL result: {str(result)}")
                self.logger.info("Finished calculating paths in the model!")

                # start pathing
                self.logger.info("Start publishing data to the portal!")
                res5 = PortalApi.update_project_data(
                    taskid="monitoring_update",
                    projectid="{}__{}".format(
                        self.model_options["projectOwner"],
                        self.model_options["projectName"].replace(" ", "_"),
                    ),
                    run_by="monitoring",
                    branch_name=self.pathing_options["model_options"]["branchName"],
                    version=int(time.time()),
                )
                self.logger.info(f"Finsihed publishing data to the portal! {res5}")

            return ret
            """

            # Propagation
            #merge = Subject()


            # Portal Update
            portal_delta = (model_committed
                #.tap(lambda i: self.logger.info('Parameter i: %s' % i))
                .tap(lambda i: self.logger.info(
                    'Start updating the %s model on the portal!' % i['branchName']
                ))
                .map(lambda i: PortalApi
                    .update_project_model_async(
                        taskid='monitoring_update'
                        , projectid='{0}__{1}'.format(
                            self.model_options['projectOwner']
                            , self.model_options['projectName'].replace(' ', '_'))
                        , run_by='monitoring'
                        , branch_name=i['branchName']
                        , version=i['query'].version))
                .tap(lambda i: self.logger.info(
                    'Finished updating the %s model on the portal!' % i['branchName']
                ))
                .retry(retry_count=3))

            portal_data = (propagation_committed
                .tap(lambda i: self.logger.info(
                    'Updating data for the %s model on the portal!' % i['branchName']
                ))
                .map(lambda i: PortalApi
                    .update_project_data(
                        taskid='monitoring_update'
                        , projectid='{0}__{1}'.format(
                            self.model_options['projectOwner']
                            , self.model_options['projectName'].replace(' ', '_'))
                        , run_by='monitoring'
                        , branch_name=i['branchName']
                        , version=int(time.time())))
                .retry(retry_count=3))

            def log_exception(e):
                self.logger.exception(e)
                return Observable.empty()
            # END log_exception
            """

        # END do_run

        """
        self.merge_coordinator\
            .tap(lambda i: self.logger.info(
                'Call merge_coordinator with len {0}!'
                .format(len(i['branchList']))
            ))\
            .tap(lambda x: self.handle_merge(x['branchList'],x['first'],'union_upload'))\
            .filter(lambda x: x['branchList']==[])\
            .tap(lambda value: print(
                "Merge Coordinator: completed merge operation {0}".format(value)))\
            .tap(lambda x: self.propagate_coordinator.on_next(Observable.of("start")))\
            .subscribe(on_next=lambda x: self.logger.info('merge_coordinator completed'),
                on_error=lambda e: self.logger.exception(
                    "Merge Coordinator: not ok: {0}".format(e)))

        self.propagate_coordinator\
            .tap(lambda i: self.logger.info('Call propagate_coordinator!'))\
            .share()\
            .replay(lambda i: i, buffer_size=1)
#            .subscribe(
#                on_next=lambda x: self.logger.info(
#                    'propagate_coordinator run completed!'
#                ),
#                on_error=lambda e: self.logger.exception(
#                    "Merge Coordinator: not ok: {0}".format(e)
#                )
#            )
        """
        return do_run(self.only_status)

    # END monitor


# END Monitoring
