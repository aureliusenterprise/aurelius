import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { faArrowLeft, faDownload, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { ShellService } from '@models4insight/shell';
import { getQueryParametersFromUrl } from '@models4insight/utils';
import { Dictionary } from 'lodash';
import { Observable } from 'rxjs';
import { ModelCompareService } from './model-compare.service';
import { map } from 'rxjs/operators';

@Component({
  selector: 'models4insight-model-compare',
  templateUrl: 'model-compare.component.html',
  styleUrls: ['model-compare.component.scss']
})
export class ModelCompareComponent implements OnInit, OnDestroy {
  readonly faArrowLeft = faArrowLeft;
  readonly faDownload = faDownload;

  bucketMapping$: Observable<Dictionary<string>>;
  isComparingModels$: Observable<boolean>;
  selectedView$: Observable<string>;

  faSpinner = faSpinner;
  previousRoute: string;

  constructor(
    private readonly modelCompareService: ModelCompareService,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly shellService: ShellService
  ) {}

  ngOnInit() {
    this.shellService
      .get('previousRoute', { includeFalsy: true })
      .then(previousRoute => (this.previousRoute = previousRoute));

    this.bucketMapping$ = this.modelCompareService.select(
      'differencePerConceptId'
    );

    this.isComparingModels$ = this.modelCompareService.select(
      'isComparingModels'
    );

    this.selectedView$ = this.route.queryParamMap.pipe(
      map(params => params.get('view'))
    );
  }

  ngOnDestroy() {}

  goBack() {
    if (this.previousRoute) {
      const [path] = this.previousRoute.split('?');

      const queryParams = this.previousRoute
        ? getQueryParametersFromUrl(this.previousRoute)
        : {};

      this.router.navigate([path], {
        queryParams
      });
    }
  }

  updateViewSelection(view: string) {
    this.router.navigate(['compare'], {
      relativeTo: this.route.parent.parent,
      queryParams: {
        view
      },
      queryParamsHandling: 'merge'
    });
  }
}
