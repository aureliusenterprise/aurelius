import { CdkVirtualScrollViewport } from '@angular/cdk/scrolling';
import { Component, OnInit, ViewChild } from '@angular/core';
import { Conflict, ConflictResolutionTemplateEnum } from '@models4insight/repository';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import { ConflictResolutionService, SaveContext } from '../conflict-resolution.service';
import { ConflictSetContext } from '@models4insight/services/model';

@Component({
  selector: 'models4insight-conflict-list',
  templateUrl: 'conflict-list.component.html',
  styleUrls: ['conflict-list.component.scss']
})
export class ConflictListComponent implements OnInit {

  readonly ConflictResolutionTemplateEnum = ConflictResolutionTemplateEnum;
  
  @ViewChild(CdkVirtualScrollViewport, {static: false}) viewport: CdkVirtualScrollViewport;

  currentContext$: Observable<ConflictSetContext>;
  conflicts$: Observable<Conflict[]>;
  selectedConflict$: Observable<Conflict>;
  selectedTemplate$: Observable<ConflictResolutionTemplateEnum | 'manual'>;
  appliedTemplate$: Observable<ConflictResolutionTemplateEnum | 'manual'>;
  resolvedConflictsCnt$: Observable<number>;
  isLoading$: Observable<boolean>;
  publishToPortal$: Observable<boolean>;

  constructor(private conflictResolutionService: ConflictResolutionService) {}

  ngOnInit() {
    this.currentContext$ = this.conflictResolutionService.select('currentContext');
    this.conflicts$ = this.conflictResolutionService.select('conflictList');
    this.selectedConflict$ = this.conflictResolutionService.select('selectedConflict').pipe(shareReplay(1));
    this.selectedTemplate$ = this.conflictResolutionService.select('selectedTemplate').pipe(shareReplay(1));
    this.appliedTemplate$ = this.conflictResolutionService.select('appliedTemplate').pipe(shareReplay(1));
    this.resolvedConflictsCnt$ = this.conflictResolutionService
      .select('resolvedConflictsCount', { includeFalsy: true })
      .pipe(shareReplay(1));
    this.isLoading$ = this.conflictResolutionService.select('isLoadingConflicts');
  }

  nextBatch(offset: number): void {
    const end = this.viewport.getRenderedRange().end;
    const total = this.viewport.getDataLength();

    if (end === total) {
      this.conflictResolutionService.nextBatch(offset);
    }
  }

  set selectedConflict(conflict: Conflict) {
    this.conflictResolutionService.update({
      description: 'New conflict selection available',
      payload: {
        selectedConflict: conflict
      }
    });
  }

  selectTemplate(event: Event) {
    this.conflictResolutionService.update({
      description: 'Selected a new template',
      payload: {
        selectedTemplate: event.srcElement['value']
      }
    });
  }

  applySelectedTemplate() {
    this.conflictResolutionService.applySelectedTemplate();
  }

  classifyConflict(conflict: Conflict) {
    return this.conflictResolutionService.classifyConflict(conflict);
  }

  handleSave(context: ConflictSetContext, save: SaveContext) {
    this.conflictResolutionService.save(context, save);
  }

  onResolveClicked() {
    this.conflictResolutionService.resolveConflicts();
  }

  trackByIndex(i: number) {
    return i;
  }
}
