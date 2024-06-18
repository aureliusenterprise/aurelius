import { Component, OnInit } from '@angular/core';
import {
  TaskContext,
  TaskManagerService,
  TaskState,
} from '@models4insight/task-manager';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Component({
  selector: 'models4insight-pipeline',
  templateUrl: './pipeline.component.html',
  styleUrls: ['./pipeline.component.css'],
})
export class PipelineComponent implements OnInit {
  tasks$: Observable<TaskContext[]>;

  constructor(private taskManager: TaskManagerService) {}

  ngOnInit() {
    // Select the tasks from the task manager that are not pending
    this.tasks$ = this.taskManager
      .select('tasks')
      .pipe(
        map((tasks) =>
          Object.values(tasks).filter(
            (task) => task.currentState !== TaskState.PENDING
          )
        )
      );
  }
}
