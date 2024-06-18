import {
  Component,
  EventEmitter,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { faCog } from '@fortawesome/free-solid-svg-icons';
import {
  CommitModelService,
  CommitOptions,
} from '@models4insight/services/model';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import { CommitOptionsModalComponent } from './commit-options-modal/commit-options-modal.component';

@Component({
  selector: 'models4insight-commit-button',
  templateUrl: 'commit-button.component.html',
  styleUrls: ['commit-button.component.scss'],
})
export class CommitButtonComponent implements OnInit {
  @Output() readonly commit = new EventEmitter<CommitOptions>();

  @ViewChild(CommitOptionsModalComponent, { static: true })
  readonly commitOptionsModal: CommitOptionsModalComponent;

  readonly faCog = faCog;

  isCommittingModel$: Observable<boolean>;

  constructor(private readonly commitModelService: CommitModelService) {}

  ngOnInit() {
    this.isCommittingModel$ = this.commitModelService
      .select('isCommittingModel')
      .pipe(shareReplay());
  }

  onCommitButtonClicked() {
    const formValue = this.commitOptionsModal.form.value;

    const options: CommitOptions = {
      ...formValue,
      conflictResolutionTemplate:
        formValue.conflictResolutionTemplate?.template,
      keepOriginalIds: formValue.keepOriginalIds,
    };

    this.commit.emit(options);
  }

  openCommitOptionsModal() {
    this.commitOptionsModal.activate();
  }
}
