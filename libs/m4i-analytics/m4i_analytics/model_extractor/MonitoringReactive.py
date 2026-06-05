import logging
import threading
import time

from rx import Observable  # type: ignore[attr-defined]
from rx.subjects import Subject

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
    model_generation_interval = 0
    status_retrieval_interval = 0
    status_retrieval_offset = 0
    model_query_interval = 0
    logger = logging.getLogger("Monitoring")
    merge_coordinator = Subject()
    propagate_coordinator = Subject()

    def __init__(
        self,
        extractors,
        model_options,
        portal_options,
        pathing_options,
        merge_branch_name="all",
        userid="monitoring",
        model_generation_interval=0,
        model_generation_offset=0,
        status_retrieval_interval=0,
        status_retrieval_offset=0,
        model_query_interval=1000,
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

    def handle_merge(self, branchList, first=False, conflict_resolution_template="upload_only"):
        if len(branchList) == 0:
            return {"query": None, "branchName": self.merge_branch_name}

        entry = branchList[0]
        fromBranch = entry["branchName"]
        self.logger.debug(f"Merge: process branch: {fromBranch}")
        self.logger.debug(f"Merge: first?: {str(first)}")
        newBranchList = []
        if len(branchList) > 1:
            newBranchList = branchList[1:]
        if first:
            model_commit = (
                Observable.of(
                    PlatformUtils.clone_branch(
                        fromBranchName=fromBranch,
                        toBranchName=self.merge_branch_name,
                        userid=self.userid,
                        description=f"{fromBranch} model",
                        **self.model_options,
                    )
                )
                .retry(retry_count=3)
                .tap(lambda i: self.logger.debug(f"Clone operation task id: {i.taskId}"))
                .share()
                .replay(lambda m: m, buffer_size=1)
            )
        else:
            model_commit = (
                Observable.of(
                    PlatformUtils.merge_branches(
                        fromBranchName=fromBranch,
                        toBranchName=self.merge_branch_name,
                        userid=self.userid,
                        description=f"{fromBranch} model",
                        **self.model_options,
                    )
                )
                .retry(retry_count=3)
                .tap(lambda i: self.logger.debug(f"Merge operation task id: {i.taskId}"))
                .share()
                .replay(lambda m: m, buffer_size=1)
            )

        model_query = (
            model_commit.combine_latest(
                Observable.timer(0, period=self.model_query_interval),
                lambda a, b: [a, b],
            )
            .switch_map(lambda i: Observable.of(PlatformApi.query_model(i[0].projectName, i[0].taskId)))
            .retry(retry_count=3)
            .tap(lambda q: self.logger.debug(f"Merge commit: Query state: {q.state}"))
            .filter(
                lambda q: (
                    q.state
                    in [
                        ModelQueryStateEnum.COMPLETED.value,
                        ModelQueryStateEnum.FAILURE.value,
                    ]
                )
            )
            .switch_map(
                lambda q: (
                    Observable.throw(Exception("Merge: Query state failure!"))
                    if q.state == ModelQueryStateEnum.FAILURE
                    else Observable.of(q)
                )
            )
            .take(1)
        )

        has_conflicts, no_conflicts = model_query.partition(
            lambda q: q.difResult.state == ModelQueryDifResultStateEnum.CONFLICT.value
        )

        conflict_resolution = (
            has_conflicts.with_latest_from(model_commit, lambda a, b: [a, b])
            .tap(lambda i: self.logger.info("Merge Conflict resolution: Replacing old model version"))
            .switch_map(
                lambda i: Observable.of(
                    PlatformApi.force_commit(
                        addListLeft=[],
                        addListRight=[],
                        description="merge repository version with new model "
                        f"version from branch {fromBranch}",
                        deleteListLeft=[],
                        deleteListRight=[],
                        fromBranch=fromBranch,
                        fromModelId="TRUNK",
                        projectName=i[1].projectName,
                        taskid=i[1].taskId,
                        toBranch=self.merge_branch_name,
                        toModelId="TRUNK",
                        userid=self.userid,
                        template=conflict_resolution_template,
                    )
                )
            )
            .retry(retry_count=3)
            .tap(
                lambda i: self.logger.debug(
                    f"Merge Conflict resolution: Replace operation task id: {i.taskId}"
                )
            )
            .share()
            .replay(lambda c: c, buffer_size=1)
        )

        conflict_resolution_query = (
            conflict_resolution.combine_latest(
                Observable.timer(0, period=self.model_query_interval),
                lambda a, b: [a, b],
            )
            .switch_map(lambda i: Observable.of(PlatformApi.query_model(i[0].projectName, i[0].taskId)))
            .retry(retry_count=3)
            .filter(
                lambda q: (
                    q.state
                    in [
                        ModelQueryStateEnum.COMPLETED.value,
                        ModelQueryStateEnum.FAILURE.value,
                    ]
                )
            )
            .switch_map(
                lambda q: (
                    Observable.throw(Exception("Merge Conflict Resolution: Query state failure!"))
                    if q.state == ModelQueryStateEnum.FAILURE.value
                    else Observable.of(q)
                )
            )
            .take(1)
        )

        commit_result = Observable.merge(no_conflicts, conflict_resolution_query).take_last(1)

        commit_result.tap(
            lambda s: self.logger.info(
                f"Merge_Coordinator: processign complete ! Call next step with {str(len(newBranchList))}"
            )
        ).subscribe(
            lambda s: self.merge_coordinator.on_next({"branchList": newBranchList, "first": False}),
            lambda e: self.logger.exception(e),
        )

        return commit_result.map(lambda r: {"query": r, "branchName": self.merge_branch_name})

    # END handle_commit

    def handle_commit(self, model, branch, conflict_resolution_template="upload_only"):
        model_commit = (
            Observable.of(
                ArchimateUtils.commit_model_to_repository(
                    model["model"],
                    branchName=branch,
                    userid=self.userid,
                    description=f"{branch} model",
                    **self.model_options,
                )
            )
            .retry(retry_count=3)
            .tap(lambda i: self.logger.debug(f"Commit operation task id: {i.taskId}"))
            .share()
            .replay(lambda m: m, buffer_size=1)
        )

        model_query = (
            model_commit.combine_latest(
                Observable.timer(0, period=self.model_query_interval),
                lambda a, b: [a, b],
            )
            .switch_map(lambda i: Observable.of(PlatformApi.query_model(i[0].projectName, i[0].taskId)))
            .retry(retry_count=3)
            .tap(lambda q: self.logger.debug(f"Commit: Query state: {q.state}"))
            .filter(
                lambda q: (
                    q.state
                    in [
                        ModelQueryStateEnum.COMPLETED.value,
                        ModelQueryStateEnum.FAILURE.value,
                    ]
                )
            )
            .switch_map(
                lambda q: (
                    Observable.throw(Exception("Commit: Query state failure!"))
                    if q.state == ModelQueryStateEnum.FAILURE
                    else Observable.of(q)
                )
            )
            .take(1)
        )

        has_conflicts, no_conflicts = model_query.partition(
            lambda q: q.difResult.state == ModelQueryDifResultStateEnum.CONFLICT.value
        )

        conflict_resolution = (
            has_conflicts.with_latest_from(model_commit, lambda a, b: [a, b])
            .tap(lambda i: self.logger.info("Commit: Replacing old model version"))
            .switch_map(
                lambda i: Observable.of(
                    PlatformApi.force_commit(
                        addListLeft=[],
                        addListRight=[],
                        description="replacing old model version",
                        deleteListLeft=[],
                        deleteListRight=[],
                        fromBranch=branch,
                        fromModelId=i[1].taskId,
                        projectName=i[1].projectName,
                        taskid=i[1].taskId,
                        toBranch=branch,
                        toModelId="TRUNK",
                        userid=self.userid,
                        template=conflict_resolution_template,
                    )
                )
            )
            .retry(retry_count=3)
            .tap(lambda i: self.logger.debug(f"Commit: Replace operation task id: {i.taskId}"))
            .share()
            .replay(lambda c: c, buffer_size=1)
        )

        conflict_resolution_query = (
            conflict_resolution.combine_latest(
                Observable.timer(0, period=self.model_query_interval),
                lambda a, b: [a, b],
            )
            .switch_map(lambda i: Observable.of(PlatformApi.query_model(i[0].projectName, i[0].taskId)))
            .retry(retry_count=3)
            .filter(
                lambda q: (
                    q.state
                    in [
                        ModelQueryStateEnum.COMPLETED.value,
                        ModelQueryStateEnum.FAILURE.value,
                    ]
                )
            )
            .switch_map(
                lambda q: (
                    Observable.throw(Exception("Commit: Query state failure!"))
                    if q.state == ModelQueryStateEnum.FAILURE.value
                    else Observable.of(q)
                )
            )
            .take(1)
        )

        commit_result = Observable.merge(no_conflicts, conflict_resolution_query).take_last(1)

        commit_result.subscribe(
            lambda s: self.logger.info("Model commit successful!"),
            lambda e: self.logger.exception(e),
        )

        return commit_result.map(lambda r: {"model": model, "query": r, "branchName": branch})

    # END handle_commit

    def monitor(self):
        # Create the project on the portal
        create_project = (
            Observable.of(self.logger.info("Creating the project on the portal!"))
            .tap(
                lambda i: PortalApi.create_project(
                    taskid="monitoring_create_project",
                    projectid="{}__{}".format(
                        self.model_options["projectOwner"],
                        self.model_options["projectName"].replace(" ", "_"),
                    ),
                    run_by="monitoring",
                    owner_username=self.model_options["projectOwner"],
                    owner_email=self.portal_options["project_owner_email"],
                )
            )
            .retry(retry_count=3)
            .tap(lambda i: self.logger.info("Project created!"))
            .share()
            .replay(lambda i: i, buffer_size=1)
        )

        # Make sure the branch that the models will be merged into exists by uploading an empty model to it.
        # create_merge_branch = (create_project
        #    .map(lambda i: ArchimateModel(defaultAttributeMapping=True))
        #    .tap(lambda m: m.organize())
        #    .tap(lambda m: ArchimateUtils.generate_view(m, layout=ManualLayout, path=['Views']))
        #    .map(lambda m: self.handle_commit(
        #        {'model': m}
        #        , self.merge_branch_name
        #        , conflict_resolution_template='union_repository'))
        #    .share()
        #    .replay(lambda i: i, buffer_size=1))

        # model_generation_timer = create_merge_branch.flat_map(
        #    lambda i: Observable.timer(self.model_generation_offset,
        #        self.model_generation_interval))
        # status_retrieval_timer = create_merge_branch.flat_map(
        #    lambda i: Observable.timer(self.status_retrieval_offset,
        #        self.status_retrieval_interval))
        model_generation_timer = create_project.flat_map(
            lambda i: Observable.timer(self.model_generation_offset, self.model_generation_interval)
        )
        status_retrieval_timer = create_project.flat_map(
            lambda i: Observable.timer(self.status_retrieval_offset, self.status_retrieval_interval)
        )

        def do_extract(extractor):
            try:
                return extractor.extract()
            except Exception as exc:
                self.logger.exception(f"do_extract: exception in extract() {str(exc)}")
                return None

        def do_run(data_only=False):
            # Model Extraction
            model_extractor = (
                Observable.of("Start model generation!")
                .tap(lambda t: self.logger.info(t))
                .flat_map(lambda t: Observable.from_list(self.extractors))
            )

            model = (
                model_extractor.tap(
                    lambda x: self.logger.info(f"Start generating the {x.branch_name} model!")
                )
                # .map(lambda x: x.extract())
                .map(lambda x: do_extract(x))
                .filter(lambda x: x is not None)
                .tap(lambda i: self.logger.info("Finished generating the {} model!".format(i["branchName"])))
                .share()
                .replay(lambda i: i, buffer_size=1)
            )

            model_commit = (
                model.tap(
                    lambda i: self.logger.info("Start committing the {} model!".format(i["branchName"]))
                )
                .flat_map(lambda i: self.handle_commit(i, i["branchName"]))
                .tap(lambda i: self.logger.info("Finished committing the {} model!".format(i["branchName"])))
                .share()
                .replay(lambda i: i, buffer_size=1)
            )

            metadata_commit = (
                (lambda: model_commit if not data_only else model)()
                .tap(lambda i: self.logger.info("Start uploading the {} data!".format(i["branchName"])))
                .tap(
                    lambda i: PlatformUtils.upload_model_data(
                        branchName=i["branchName"],
                        conceptData=i["model"]["data"],
                        **self.model_options,
                    )
                )
                .retry(retry_count=3)
                .tap(lambda i: self.logger.info("Finished uploading the {} data!".format(i["branchName"])))
                .share()
                .replay(lambda i: i, buffer_size=1)
            )

            model_committed = metadata_commit

            def collect(acc, i):
                acc.append(i)
                return acc

            # END collect

            committed_models = (
                model_committed.scan(collect, seed=[])
                .start_with([])
                .take_last(1)
                # .tap(lambda branchList: self.merge_coordinator.on_next(branchList.copy()))
                .share()
                .replay(lambda i: i, buffer_size=1)
            )

            # Model merge
            # merge = Subject()
            # self.merge_coordinator.tap(lambda x: self.handle_merge(x))
            #    .filter(lambda x: x==[])
            #    .tap(lambda value: print("step 1:  {0}".format(value)))
            #    .subscribe(
            #        on_next=lambda x: merge.on_next(value),
            #        on_error=lambda e: print("Step 1: not ok: {0}".format(e))
            #    )

            """
            merge = (committed_models
                #.flat_map(lambda l: Observable.from_list(l))
                #.tap(lambda i: self.logger.info(
                #    f'Start merging the {len(i)} model with the '
                #    f'{self.merge_branch_name} model!'
                #))
                .map(
                    lambda branchList: self.merge_coordinator.on_next(
                        {'branchList': branchList.copy(), 'first': True}
                    )
                )
                #.flat_map(lambda branchList: self.merge_coordinator.on_next(branchList)))
                #.tap(lambda i: self.logger.info(
                #    f'Finished merging the {len(i["branchList"])} model with '
                #    f'the {self.merge_branch_name} model!'
                #))
                .share()
                .replay(lambda i: i))
            """
            committed_models.tap(
                lambda i: self.logger.info(
                    f"Start merging the {len(i)} model with the {self.merge_branch_name} model!"
                )
            ).map(
                lambda branchList: self.merge_coordinator.on_next(
                    {"branchList": list(branchList), "first": True}
                )
            ).subscribe(lambda x: self.logger.info("Finished merging the models!"))

            # Propagation
            # merge = Subject()
            propagation = (
                self.propagate_coordinator.tap(
                    lambda i: self.logger.info(
                        "Start propagating statuses for the integrated model "
                        f"in branch {self.merge_branch_name}!"
                    )
                )
                .map(
                    lambda i: {
                        "branchName": self.merge_branch_name,
                        "propagation": propagate(
                            {
                                "projectOwner": self.model_options["projectOwner"],
                                "projectName": self.model_options["projectName"],
                                "branchName": self.merge_branch_name,
                            }
                        ),
                    }
                )
                .tap(
                    lambda i: self.logger.info(
                        f"Finished propagating statuses for integrated model in branch {i['branchName']}!"
                    )
                )
                .share()
                .replay(lambda i: i, buffer_size=1)
            )

            propagation_committed = (
                propagation.tap(
                    lambda i: self.logger.info(
                        "Start uploading the {} propagation data!".format(i["branchName"])
                    )
                )
                .tap(
                    lambda i: PlatformUtils.upload_model_data(
                        branchName=i["branchName"],
                        conceptData=i["propagation"],
                        **self.model_options,
                    )
                )
                .retry(retry_count=3)
                .tap(
                    lambda i: self.logger.info(
                        "Finished uploading the {} propagation data!".format(i["branchName"])
                    )
                )
                .share()
                .replay(lambda i: i, buffer_size=1)
            )

            def trigger_pathing():
                params = {
                    "project_name": "{}__{}".format(
                        self.model_options["projectOwner"],
                        self.model_options["projectName"],
                    ),
                    "branch_name": self.pathing_options["model_options"]["branchName"],
                    "target_table": self.pathing_options["target_table"],
                    "allowed_relations": [
                        rel["shorthand"] for rel in self.pathing_options["allowed_relationship_types"]
                    ],
                }

                result = ApiUtils.get("http://portal.models4insight.com/m4i/rest/pathing", params)
                return result

            # Pathing
            pathing = (
                propagation_committed.tap(lambda i: self.logger.info("Start processing paths in the model!"))
                .map(lambda i: trigger_pathing())
                .tap(lambda i: self.logger.info("Finished calculating paths in the model!"))
            )

            # Portal Update
            portal_delta = (
                model_committed
                # .tap(lambda i: self.logger.info('Parameter i: %s' % i))
                .tap(
                    lambda i: self.logger.info(
                        "Start updating the {} model on the portal!".format(i["branchName"])
                    )
                )
                .map(
                    lambda i: PortalApi.update_project_model_async(
                        taskid="monitoring_update",
                        projectid="{}__{}".format(
                            self.model_options["projectOwner"],
                            self.model_options["projectName"].replace(" ", "_"),
                        ),
                        run_by="monitoring",
                        branch_name=i["branchName"],
                        version=i["query"].version,
                    )
                )
                .tap(
                    lambda i: self.logger.info(
                        "Finished updating the {} model on the portal!".format(i["branchName"])
                    )
                )
                .retry(retry_count=3)
            )

            portal_data = (
                propagation_committed.tap(
                    lambda i: self.logger.info(
                        "Updating data for the {} model on the portal!".format(i["branchName"])
                    )
                )
                .map(
                    lambda i: PortalApi.update_project_data(
                        taskid="monitoring_update",
                        projectid="{}__{}".format(
                            self.model_options["projectOwner"],
                            self.model_options["projectName"].replace(" ", "_"),
                        ),
                        run_by="monitoring",
                        branch_name=i["branchName"],
                        version=int(time.time()),
                    )
                )
                .retry(retry_count=3)
            )

            def log_exception(e):
                self.logger.exception(e)
                return Observable.empty()

            # END log_exception

            return Observable.merge(portal_delta, portal_data, pathing).catch_exception(
                lambda e: log_exception(e)
            )

        # END do_run
        self.merge_coordinator.tap(
            lambda i: self.logger.info("Call merge_coordinator with len {}!".format(len(i["branchList"])))
        ).tap(lambda x: self.handle_merge(x["branchList"], x["first"], "union_upload")).filter(
            lambda x: x["branchList"] == []
        ).tap(lambda value: self.logger.info(f"Merge Coordinator: completed merge operation {value}")).tap(
            lambda x: self.propagate_coordinator.on_next(Observable.of("start"))
        ).subscribe(
            on_next=lambda x: self.logger.info("merge_coordinator completed"),
            on_error=lambda e: self.logger.exception(f"Merge Coordinator: not ok: {e}"),
        )

        self.propagate_coordinator.tap(
            lambda i: self.logger.info("Call propagate_coordinator!")
        ).share().replay(lambda i: i, buffer_size=1)

        # self.merge_coordinator\
        #    .subscribe(
        #        on_next=lambda x: self.logger.info(
        #            'LOGGING merge_coordinator with len {0}!'.format(len(x))
        #        ),
        #        on_error=lambda e: print("Step 1: not ok: {0}".format(e))
        #    )

        if not self.only_status:
            model_generation_timer.flat_map(lambda t: do_run()).subscribe(
                lambda i: self.logger.info("Model generation run completed!")
            )

        status_retrieval_timer.flat_map(lambda t: do_run(data_only=True)).subscribe(
            lambda i: self.logger.info("Status retrieval run completed!")
        )

        keep_alive = threading.Condition()
        keep_alive.acquire()
        keep_alive.wait()

    # END monitor


# END Monitoring
