import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { faStar as faRegularStar } from '@fortawesome/free-regular-svg-icons';
import { faStar as faSolidStar } from '@fortawesome/free-solid-svg-icons';
import { CompareModalComponent } from '@models4insight/components';
import { PermissionLevel, Project } from '@models4insight/repository';
import { ProjectService } from '@models4insight/services/project';
import { FavoriteProjectsService } from '@models4insight/services/user-info';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { first } from 'rxjs/operators';
import { CompareModalService } from './compare-modal.service';

@Component({
  selector: 'models4insight-project',
  templateUrl: './project.component.html',
  styleUrls: ['./project.component.scss']
})
export class ProjectComponent implements OnInit, OnDestroy {
  @ViewChild(CompareModalComponent, { static: true })
  compareModal: CompareModalComponent;

  isFavorite$: Observable<boolean>;
  project$: Observable<Project>;

  faRegularStar = faRegularStar;
  faSolidStar = faSolidStar;

  PermissionLevel = PermissionLevel;

  constructor(
    private readonly compareModalService: CompareModalService,
    private readonly favoriteProjectsService: FavoriteProjectsService,
    private readonly projectService: ProjectService,
    private readonly route: ActivatedRoute,
    private readonly router: Router
  ) {}

  ngOnInit() {
    this.project$ = this.projectService.selectCurrentProject();
    this.isFavorite$ = this.favoriteProjectsService.isCurrentProjectFavorite;

    this.compareModalService.onModalActivated
      .pipe(untilDestroyed(this))
      .subscribe(([branchName, version]) =>
        this.compareModal.activateAndPrefill(branchName, version)
      );

    this.compareModal.submission
      .pipe(untilDestroyed(this))
      .subscribe(queryParams => {
        this.router.navigate(['compare'], {
          queryParams,
          relativeTo: this.route
        });
      });
  }

  ngOnDestroy() {}

  async toggleFavorite() {
    const [project, isFavorite] = await Promise.all([
      this.projectService.getCurrentProject(),
      this.favoriteProjectsService.isCurrentProjectFavorite
        .pipe(first())
        .toPromise()
    ]);

    if (isFavorite) {
      this.favoriteProjectsService.removeFavoriteProject(project);
    } else {
      this.favoriteProjectsService.addFavoriteProject(project);
    }
  }
}
