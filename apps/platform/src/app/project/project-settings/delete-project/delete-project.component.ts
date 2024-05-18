import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ProjectService, ProjectsService } from '@models4insight/services/project';
import { Observable } from 'rxjs';
import { first } from 'rxjs/operators';

@Component({
  selector: 'models4insight-delete-project-settings',
  templateUrl: 'delete-project.component.html',
  styleUrls: ['delete-project.component.scss']
})
export class DeleteProjectSettingsComponent implements OnInit {
  isDeletingProject$: Observable<boolean>;

  constructor(
    private readonly projectService: ProjectService,
    private readonly projectsService: ProjectsService,
    private readonly router: Router
  ) {}

  ngOnInit() {
    this.isDeletingProject$ = this.projectsService.select('isDeletingProject');
  }

  async deleteProject(event: boolean) {
    if (event) {
      const projectDeleted = this.projectsService.onProjectDeleted
        .pipe(first())
        .toPromise();

      this.projectService.deleteCurrentProject();

      // After deleting the project, navigate to the projects page
      await projectDeleted;

      return this.router.navigate(['projects']);
    }
  }
}
