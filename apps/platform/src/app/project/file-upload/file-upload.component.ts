import { Component, OnDestroy, OnInit } from '@angular/core';
import { UntypedFormBuilder, UntypedFormControl, UntypedFormGroup } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { BranchSelect, defaultBranchSelectContext, defaultDescriptionInputContext, defaultFileDropzoneContext, DescriptionInput, DescriptionInputContext, FileDropzone, FileDropzoneContext, SelectContext } from '@models4insight/components';
import { PermissionLevel, Project } from '@models4insight/repository';
import { BranchesService } from '@models4insight/services/branch';
import { CommitModelService, CommitOptions } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { filter, switchMap } from 'rxjs/operators';

const branchSelectContext: SelectContext = {
  ...defaultBranchSelectContext,
  requiredErrorMessage: 'Please select a branch for your upload'
};

const descriptionContext: DescriptionInputContext = {
  ...defaultDescriptionInputContext,
  label: 'Comment',
  placeholder: 'Comment',
  requiredErrorMessage: 'Please provide a comment for your upload'
};

const modelUploadContext: FileDropzoneContext = {
  ...defaultFileDropzoneContext,
  title: 'Model upload'
};

@Component({
  selector: 'models4insight-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent implements OnInit, OnDestroy {
  readonly PermissionLevel = PermissionLevel;

  readonly branchSelectContext = branchSelectContext;
  readonly descriptionContext = descriptionContext;
  readonly modelUploadContext = modelUploadContext;

  project$: Observable<Project>;
  isModalActive$: Observable<boolean>;
  isCommitingModel$: Observable<boolean>;

  fileUploadForm: UntypedFormGroup;
  isSubmitted = false;

  constructor(
    private readonly branchesService: BranchesService,
    private readonly formBuilder: UntypedFormBuilder,
    private readonly commitModelService: CommitModelService,
    private readonly projectService: ProjectService,
    private readonly route: ActivatedRoute
  ) {
    this.createForms();
  }

  ngOnInit() {
    this.route.queryParamMap
      .pipe(
        switchMap(queryParams =>
          this.branchesService.getBranchByName(queryParams.get('toBranch'))
        ),
        filter(branch => !!branch),
        untilDestroyed(this)
      )
      .subscribe(branch =>
        this.fileUploadForm.patchValue({
          branch
        })
      );

    // Whenever a model is committed, clear the form
    this.commitModelService.onModelCommitted
      .pipe(untilDestroyed(this))
      .subscribe(() => this.fileUploadForm.reset());

    this.project$ = this.projectService.selectCurrentProject();
    this.isCommitingModel$ = this.commitModelService.select(
      'isCommittingModel'
    );
  }

  ngOnDestroy() {}

  createForms() {
    this.fileUploadForm = this.formBuilder.group({
      file: new FileDropzone(['archimate']),
      branch: new BranchSelect(),
      comment: new DescriptionInput(),
      publishToPortal: new UntypedFormControl(false)
    });
  }

  onCommit(options: CommitOptions) {
    this.isSubmitted = true;
    this.fileUploadForm.updateValueAndValidity();
    if (this.fileUploadForm.valid) {
      const { branch, comment, file } = this.fileUploadForm.value;
      this.commitModelService.commitModel(branch.name, comment, file, options);
      this.isSubmitted = false;
    }
  }
}
