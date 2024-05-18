import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { UntypedFormBuilder, UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { BranchSelect, CreateBranchModalComponent, defaultBranchSelectContext, defaultDescriptionInputContext, DescriptionInputContext } from '@models4insight/components';
import { Branch, PermissionLevel, Project } from '@models4insight/repository';
import { BranchesService } from '@models4insight/services/branch';
import { ProjectService } from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { filter, shareReplay, switchMap } from 'rxjs/operators';
import { BranchMergeService } from './branch-merge.service';

// Validator for the branch merge form which checks whether the from and to branches are different
const branchNamesDiffer = (control: UntypedFormGroup) => {
  const fromBranch = control.get('fromBranch').value;
  const toBranch = control.get('toBranch').value;
  return !!fromBranch && !!toBranch && fromBranch.name === toBranch.name
    ? { branchNamesMatch: true }
    : null;
};

const descriptionContext: DescriptionInputContext = {
  ...defaultDescriptionInputContext,
  label: 'Comment',
  placeholder: 'Comment',
  requiredErrorMessage: 'Please provide a comment that describes the move'
};

const fromBranchSelectContext = {
  ...defaultBranchSelectContext,
  label: 'From branch',
  requiredErrorMessage: 'Please select a branch to move from'
};

const toBranchSelectContext = {
  ...defaultBranchSelectContext,
  label: 'To branch',
  requiredErrorMessage: 'Please select a branch to move to'
};

@Component({
  selector: 'models4insight-branch-merge',
  templateUrl: 'branch-merge.component.html',
  styleUrls: ['branch-merge.component.scss']
})
export class BranchMergeComponent implements OnInit, OnDestroy {
  readonly descriptionContext = descriptionContext;
  readonly fromBranchSelectContext = fromBranchSelectContext;
  readonly toBranchSelectContext = toBranchSelectContext;

  readonly PermissionLevel = PermissionLevel;

  project$: Observable<Project>;
  branches$: Observable<Branch[]>;
  isMoveBranchesFormSubmitted$: Observable<boolean>;
  isMovingBranches$: Observable<boolean>;

  branchMergeForm: UntypedFormGroup;

  @ViewChild(CreateBranchModalComponent, { static: true })
  private readonly editBranchModal: CreateBranchModalComponent;

  constructor(
    private readonly branchesService: BranchesService,
    private readonly branchMergeService: BranchMergeService,
    private readonly formBuilder: UntypedFormBuilder,
    private readonly projectService: ProjectService,
    private readonly route: ActivatedRoute
  ) {
    this.createForm();
  }

  ngOnInit() {
    this.route.queryParamMap.pipe(untilDestroyed(this)).subscribe(params =>
      this.branchMergeService.update({
        description: 'New form parameters available',
        payload: {
          fromBranch: params.get('fromBranch'),
          toBranch: params.get('toBranch')
        }
      })
    );

    this.branchMergeService
      .select('fromBranch')
      .pipe(
        filter(branchName => !!branchName),
        switchMap(fromBranch =>
          this.branchesService.getBranchByName(fromBranch)
        ),
        filter(branch => !!branch),
        untilDestroyed(this)
      )
      .subscribe(fromBranch =>
        this.branchMergeForm.patchValue({
          fromBranch
        })
      );

    this.branchMergeService
      .select('toBranch')
      .pipe(
        filter(branchName => !!branchName),
        switchMap(toBranch => this.branchesService.getBranchByName(toBranch)),
        filter(branch => !!branch),
        untilDestroyed(this)
      )
      .subscribe(toBranch =>
        this.branchMergeForm.patchValue({
          toBranch
        })
      );

    this.branchMergeService
      .select('isMoveBranchesFormSubmitted')
      .pipe(
        filter(state => !state),
        untilDestroyed(this)
      )
      .subscribe(() => this.branchMergeForm.reset());

    this.project$ = this.projectService.selectCurrentProject();

    this.branches$ = this.branchesService.branches;

    this.isMovingBranches$ = this.branchMergeService.select('isMovingBranches');

    this.isMoveBranchesFormSubmitted$ = this.branchMergeService
      .select('isMoveBranchesFormSubmitted')
      .pipe(shareReplay());
  }

  ngOnDestroy() {}

  createForm() {
    this.branchMergeForm = this.formBuilder.group(
      {
        fromBranch: new BranchSelect(),
        toBranch: new BranchSelect(),
        comment: new UntypedFormControl('', {
          validators: [Validators.required]
        })
      },
      { validator: branchNamesDiffer }
    );
  }

  editBranch(branch: Branch) {
    this.editBranchModal.subject = branch;
    this.editBranchModal.activate();
  }

  startMerge() {
    this.branchMergeService.update({
      description: 'Merge form submitted',
      payload: {
        isMoveBranchesFormSubmitted: true
      }
    });
    this.branchMergeForm.updateValueAndValidity();
    if (this.branchMergeForm.valid) {
      const { fromBranch, toBranch, comment } = this.branchMergeForm.value;
      this.branchMergeService.moveBranches(
        fromBranch.name,
        toBranch.name,
        comment
      );
    }
  }

  trackByBranchId(branch: Branch) {
    return branch.id;
  }
}
