import { Component, OnDestroy, OnInit } from '@angular/core';
import { UntypedFormGroup } from '@angular/forms';
import { faSearch } from '@fortawesome/free-solid-svg-icons';
import { BranchSelect, ProjectSelect, ProvenanceSelect, SortableTableShellConfig } from '@models4insight/components';
import { Branch, MetricExemption, ModelProvenance, Project } from '@models4insight/repository';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { ExemptionsService } from './exemptions.service';

const exemptionsTableConfig: SortableTableShellConfig<MetricExemption> = {
  concept_id: {
    displayName: 'Concept id',
    description:
      'The unique identifier of the concept to which this exemption applies'
  },
  metric: {
    displayName: 'Metric name',
    description: 'The name of the metric to which this exemption applies'
  },
  branch: {
    displayName: 'Branch id',
    description:
      'The unique identifier of the branch to which this exemption applies'
  },
  version: {
    displayName: 'Timestamp',
    description:
      'The timestamp of the model version to which this exemption applies',
    isTimestamp: true
  },
  comment: {
    displayName: 'Description',
    description: 'A description of the exemption'
  }
};

@Component({
  selector: 'models4insight-exemptions',
  templateUrl: 'exemptions.component.html',
  styleUrls: ['exemptions.component.scss'],
  providers: [ExemptionsService]
})
export class ExemptionsComponent implements OnInit, OnDestroy {
  readonly exemptionsTableConfig = exemptionsTableConfig;
  readonly faSearch = faSearch;

  branches$: Observable<Branch[]>;
  exemptions$: Observable<MetricExemption[]>;
  isLoadingExemptions$: Observable<boolean>;
  projects$: Observable<Project[]>;
  versions$: Observable<ModelProvenance[]>;

  searchForm: UntypedFormGroup;

  constructor(
    private readonly exemptionsService: ExemptionsService,
  ) {
    this.initForm();
  }

  ngOnInit() {
    this.branches$ = this.exemptionsService.select('branches');
    this.exemptions$ = this.exemptionsService.select('exemptions');
    this.isLoadingExemptions$ = this.exemptionsService.select(
      'isLoadingExemptions'
    );
    this.versions$ = this.exemptionsService.select('versions');
  }

  ngOnDestroy() {}

  findExemptions() {
    const { project, branch, version } = this.searchForm.value;
    this.exemptionsService.loadExemptions(project, branch, version);
  }

  private initForm() {
    const projectSelect = new ProjectSelect(),
      branchSelect = new BranchSelect(),
      versionSelect = new ProvenanceSelect();

    projectSelect.valueChanges.pipe(untilDestroyed(this)).subscribe(project => {
      this.exemptionsService.loadBranches(project);
      branchSelect.reset();
      versionSelect.reset();
    });

    branchSelect.valueChanges.pipe(untilDestroyed(this)).subscribe(branch => {
      this.exemptionsService.loadVersions(projectSelect.value, branch);
      versionSelect.reset();
    });

    this.searchForm = new UntypedFormGroup({
      project: projectSelect,
      branch: branchSelect,
      version: versionSelect
    });
  }
}
