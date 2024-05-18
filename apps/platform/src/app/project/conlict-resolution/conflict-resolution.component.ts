import { Component, OnInit } from '@angular/core';
import { ConflictsService, ConflictSetContext } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { ConflictResolutionService } from './conflict-resolution.service';

@Component({
  selector: 'models4insight-conflict-resolution',
  templateUrl: 'conflict-resolution.component.html',
  styleUrls: ['conflict-resolution.component.scss']
})
export class ConflictResolutionComponent implements OnInit {
  conflictSets$: Observable<ConflictSetContext[]>;
  currentContext$: Observable<ConflictSetContext>;

  constructor(
    private projectService: ProjectService,
    private conflictsService: ConflictsService,
    private conflictResolutionService: ConflictResolutionService
  ) {}

  ngOnInit() {
    this.conflictSets$ = this.projectService
      .select('projectId')
      .pipe(
        switchMap(projectId =>
          this.conflictsService.selectConflictSetsForProject(projectId)
        )
      );

    this.currentContext$ = this.conflictResolutionService.select(
      'currentContext',
      { includeFalsy: true }
    );
  }

  set currentContext(context: ConflictSetContext) {
    this.conflictResolutionService.update({
      description: 'New current context available',
      payload: {
        currentContext: context
      }
    });
  }
}
