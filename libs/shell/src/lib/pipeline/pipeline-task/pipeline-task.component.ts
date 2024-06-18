import {
  Component,
  Inject,
  Input,
  OnDestroy,
  OnInit,
  Optional,
} from '@angular/core';
import { Router } from '@angular/router';
import { faArrowRight, faBug } from '@fortawesome/free-solid-svg-icons';
import { AuthenticationService } from '@models4insight/authentication';
import { StoreService } from '@models4insight/redux';
import { reportError } from '@models4insight/repository';
import {
  TaskContext,
  TaskManagerService,
  TaskState,
} from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { VersionService } from '@models4insight/version';
import { Subject } from 'rxjs';
import { exhaustMap } from 'rxjs/operators';
import { ShellConfig, ShellConfigService } from '../../shell-config.service';

@Component({
  selector: 'models4insight-pipeline-task',
  templateUrl: './pipeline-task.component.html',
  styleUrls: ['./pipeline-task.component.scss'],
})
export class PipelineTaskComponent implements OnInit, OnDestroy {
  readonly TaskState = TaskState;

  readonly faArrowRight = faArrowRight;
  readonly faBug = faBug;

  private readonly report$: Subject<void> = new Subject<void>();

  isReporting = false;
  hasBeenReported = false;

  constructor(
    private authenticationService: AuthenticationService,
    private router: Router,
    private taskManager: TaskManagerService,
    private storeService: StoreService,
    private versionService: VersionService,
    @Optional() @Inject(ShellConfigService) private config: ShellConfig = {}
  ) {}

  @Input() task: TaskContext;

  ngOnInit() {
    this.report$
      .pipe(
        exhaustMap(() => this.handleReportError()),
        untilDestroyed(this)
      )
      .subscribe();
  }

  ngOnDestroy() {}

  clear() {
    this.taskManager.clearTask(this.task.id);
  }

  navigate() {
    const { route, relativeTo } = this.task.currentNavigationContext;
    this.router
      .navigate(route, { relativeTo: relativeTo })
      .then(() => this.clear());
  }

  report() {
    this.report$.next();
  }

  private async handleReportError() {
    this.isReporting = true;

    const username = await this.authenticationService.get([
      'credentials',
      'username',
    ]);

    try {
      await reportError(
        this.config.appName,
        this.versionService.appVersion,
        this.task.error,
        username,
        this.storeService.snapshot
      ).toPromise();
    } finally {
      this.hasBeenReported = true;
      this.isReporting = false;
    }
  }
}
