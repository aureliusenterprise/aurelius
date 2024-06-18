import { Component, OnInit, Type, ViewChild } from '@angular/core';
import { BaseQuickview, QuickviewComponent } from '@models4insight/components';
import { untilDestroyed } from '@models4insight/utils';
import { identity } from 'lodash';
import { Observable, partition } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import { ModelExplorerService } from '../model-explorer.service';
import { ModelviewService } from '../model-view.service';
import { ModelBrowserBrowseComponent } from './browse/browse.component';
import { ModelBrowserModelComponent } from './model/model.component';
import { ModelBrowserSelectionComponent } from './selection/selection.component';
import { ModelBrowserViewComponent } from './view/view.component';

type ModelBrowserTab = 'browse' | 'model' | 'selection' | 'view';

interface TabDefinition {
  readonly id: ModelBrowserTab;
  readonly component: Type<any>;
  readonly displayName: string;
  readonly condition?: Observable<any>;
}

@Component({
  selector: 'models4insight-model-browser',
  templateUrl: 'model-browser.component.html',
  styleUrls: ['model-browser.component.scss'],
})
export class ModelBrowserComponent extends BaseQuickview implements OnInit {
  @ViewChild(QuickviewComponent, { static: true })
  quickview: QuickviewComponent;

  tabs: { [key in ModelBrowserTab]: TabDefinition };
  currentTab: TabDefinition;

  private selectedEntity$: Observable<string>;
  private selectedView$: Observable<string>;

  private previousTab: ModelBrowserTab;

  constructor(
    private readonly modelExplorerService: ModelExplorerService,
    private readonly modelviewService: ModelviewService
  ) {
    super();
  }

  ngOnInit() {
    this.selectedEntity$ = this.modelExplorerService
      .select('selectedEntity', {
        includeFalsy: true,
      })
      .pipe(shareReplay());

    this.selectedView$ = this.modelviewService
      .select('viewId', {
        includeFalsy: true,
      })
      .pipe(shareReplay());

    this.initTabs();

    const [entitySelected, entityDeselected] = partition(
      this.selectedEntity$,
      identity
    );

    entitySelected.pipe(untilDestroyed(this)).subscribe(() => {
      this.selectTab('selection');
      this.open();
    });

    entityDeselected.pipe(untilDestroyed(this)).subscribe(() => {
      this.close();
      if (this.currentTab.id === 'selection') {
        this.selectTab(this.previousTab);
      }
    });

    const [viewSelected, viewDeselected] = partition(
      this.selectedView$,
      identity
    );

    viewSelected.pipe(untilDestroyed(this)).subscribe(() => {
      this.close();
    });

    viewDeselected.pipe(untilDestroyed(this)).subscribe(() => {
      this.selectTab('browse');
      this.open();
    });
  }

  preserveKeyOrder() {
    return 0;
  }

  selectTab(id: ModelBrowserTab) {
    if (this.currentTab.id !== id) {
      this.previousTab = this.currentTab.id;
      this.currentTab = this.tabs[id];
    }
  }

  private initTabs() {
    this.tabs = {
      browse: {
        id: 'browse',
        component: ModelBrowserBrowseComponent,
        displayName: 'Browse',
      },
      model: {
        id: 'model',
        component: ModelBrowserModelComponent,
        displayName: 'Model',
      },
      view: {
        id: 'view',
        component: ModelBrowserViewComponent,
        displayName: 'View',
        condition: this.selectedView$,
      },
      selection: {
        id: 'selection',
        component: ModelBrowserSelectionComponent,
        displayName: 'Selection',
        condition: this.selectedEntity$,
      },
    };

    this.currentTab = this.tabs['browse'];
  }
}
