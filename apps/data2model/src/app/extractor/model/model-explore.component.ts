import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { faEllipsisH, faFilter, faSearch } from '@fortawesome/free-solid-svg-icons';
import { Feature } from '@models4insight/permissions';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { ExtractorService } from '../extractor.service';
import { CommitModalComponent } from './commit-modal/commit-modal.component';

@Component({
  selector: 'models4insight-explore',
  templateUrl: 'model-explore.component.html',
  styleUrls: ['model-explore.component.scss']
})
export class ModelExploreComponent implements OnInit, OnDestroy {
  @ViewChild(CommitModalComponent, { static: true })
  private readonly commitModal: CommitModalComponent;
  readonly Feature = Feature;

  readonly faEllipsisH = faEllipsisH;
  readonly faFilter = faFilter;
  readonly faSearch = faSearch;

  isCommittingModel$: Observable<boolean>;

  constructor(private readonly extractorService: ExtractorService) {}

  ngOnInit() {
    this.isCommittingModel$ = this.extractorService.select('isCommitingModel');

    this.commitModal.submission
      .pipe(untilDestroyed(this))
      .subscribe(commit => this.extractorService.commitModel(commit));
  }

  ngOnDestroy() {}

  activateCommitModal() {
    this.commitModal.activate();
  }
}
