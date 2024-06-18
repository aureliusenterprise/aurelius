import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { TreeComponent } from '@models4insight/components';
import { untilDestroyed } from '@models4insight/utils';
import { Dictionary, set } from 'lodash';
import { combineLatest, Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { ModelExplorerService } from '../../model-explorer.service';
import { ModelviewService } from '../../model-view.service';
import { ModelView } from '../../parsers';

@Component({
  selector: 'models4insight-model-browser-browse',
  templateUrl: 'browse.component.html',
  styleUrls: ['browse.component.scss'],
})
export class ModelBrowserBrowseComponent implements OnInit, OnDestroy {
  @ViewChild(TreeComponent, { static: true })
  private readonly modelTree: TreeComponent;

  constructor(
    private readonly modelExplorerService: ModelExplorerService,
    private readonly modelviewService: ModelviewService
  ) {}

  ngOnInit() {
    combineLatest([
      this.modelExplorerService.select('views'),
      this.modelExplorerService.select('organizations'),
    ])
      .pipe(
        switchMap(([views, organizations]) =>
          this.buildViewPathIndex(views, organizations)
        ),
        untilDestroyed(this)
      )
      .subscribe((index) => (this.modelTree.pathIndex = index));

    this.modelviewService
      .select('viewId')
      .pipe(untilDestroyed(this))
      .subscribe((selectedView) => (this.modelTree.activeNode = selectedView));

    this.modelTree.nodeActivated
      .pipe(untilDestroyed(this))
      .subscribe((id) => (this.selectedView = id));
  }

  ngOnDestroy() {}

  set selectedView(viewId: string) {
    this.modelviewService.viewId = viewId;
  }

  get isBuildingTree(): Observable<boolean> {
    return this.modelTree.isBuildingTree;
  }

  private async buildViewPathIndex(
    views: Dictionary<ModelView>,
    organizations: Dictionary<string>
  ) {
    const viewPathIndex = {};
    for (const [viewId, view] of Object.entries(views)) {
      set(
        viewPathIndex,
        `${organizations[viewId]}/${view.name}`.split('/'),
        viewId
      );
    }
    return viewPathIndex;
  }
}
