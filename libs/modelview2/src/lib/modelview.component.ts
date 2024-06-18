import {
  Component,
  ElementRef,
  Input,
  OnDestroy,
  OnInit,
  ViewChild,
} from '@angular/core';
import {
  faArrowsAlt,
  faCamera,
  faExpand,
  faInfo,
  faSearch,
  faSpinner,
} from '@fortawesome/free-solid-svg-icons';
import { ModelService } from '@models4insight/services/model';
import { ProjectService } from '@models4insight/services/project';
import { saveAsFile, untilDestroyed } from '@models4insight/utils';
import JSZip from 'jszip';
import { Dictionary } from 'lodash';
import { Observable } from 'rxjs';
import { ColorPallette, ColorViewService } from './color-view.service';
import { ModelBrowserComponent } from './model-browser/model-browser.component';
import { ModelExplorerService } from './model-explorer.service';
import { ModelviewService } from './model-view.service';
import { ModelViewConnection, ModelViewNode } from './parsers';
import { SaveViewAsImageService } from './save-view-as-image.service';
import { RelationDef } from './shapes/types';
import { SVGZoomDirective } from './svg-zoom.directive';

@Component({
  selector: 'models4insight-modelview2',
  templateUrl: './modelview.component.html',
  styleUrls: ['./modelview.component.scss'],
  providers: [
    ColorViewService,
    ModelExplorerService,
    ModelviewService,
    SaveViewAsImageService,
  ],
})
export class ModelviewComponent implements OnInit, OnDestroy {
  readonly faArrowsAlt = faArrowsAlt;
  readonly faCamera = faCamera;
  readonly faExpand = faExpand;
  readonly faInfo = faInfo;
  readonly faSearch = faSearch;
  readonly faSpinner = faSpinner;

  @ViewChild(ModelBrowserComponent, { static: false })
  browser: ModelBrowserComponent;

  @ViewChild('svg', { static: false })
  svg: ElementRef<SVGElement>;

  @ViewChild('zoomTarget', { static: false })
  viewContainer: ElementRef<SVGGraphicsElement>;

  private _zoom: SVGZoomDirective;

  connections$: Observable<ModelViewConnection[]>;
  defs$: Observable<Dictionary<RelationDef>>;
  description$: Observable<string>;
  displayName$: Observable<string>;
  isConverting$: Observable<boolean>;
  isLoadingModel$: Observable<boolean>;
  isParsingModel$: Observable<boolean>;
  modelName$: Observable<string>;
  nodes$: Observable<ModelViewNode[]>;

  isFullscreen = false;

  constructor(
    private readonly colorViewService: ColorViewService,
    private readonly modelExplorerService: ModelExplorerService,
    private readonly modelService: ModelService,
    private readonly modelviewService: ModelviewService,
    private readonly projectService: ProjectService,
    private readonly saveViewAsImageService: SaveViewAsImageService
  ) {}

  ngOnInit() {
    this.connections$ = this.modelviewService.connections;
    this.defs$ = this.modelviewService.select('defs');
    this.description$ = this.modelviewService.description;
    this.displayName$ = this.modelviewService.displayName;
    this.isConverting$ = this.saveViewAsImageService.select('isConverting');
    this.isLoadingModel$ = this.modelService.select('isLoadingModel');
    this.isParsingModel$ = this.modelExplorerService.select('isParsingModel');
    this.modelName$ = this.modelExplorerService.select(['info', 'name']);
    this.nodes$ = this.modelviewService.nodes;

    // Adds a console only function to save all views as images
    window['saveAllViewsAsImages'] = (delay: number = 50) => {
      this.saveAllViewsAsImages(delay);
      return 'Saving all views as images...';
    };
  }

  ngOnDestroy() {
    delete window['saveAllViewsAsImages'];
  }

  openBrowser() {
    this.browser.open();
  }

  openViewInfo() {
    this.browser.selectTab('view');
    this.openBrowser();
  }

  resetZoom() {
    if (this.zoom) {
      this.zoom.resetZoom();
    }
  }

  async saveAllViewsAsImages(delay: number) {
    const zoomLevel = this.zoom.resetZoom();

    const [currentViewId, viewsById] = await Promise.all([
      this.modelviewService.get('viewId'),
      this.modelExplorerService.get('views'),
    ]);

    const zip = new JSZip();

    for (const [id, view] of Object.entries(viewsById)) {
      this.modelviewService.viewId = id;

      // Wait for the view to draw... ugly solution since the time required depends heavily on the complexity of the view
      // When the delay is too short, the previous view may still be present in the DOM and therefore saved again under the wrong name.
      await new Promise((resolve) => setTimeout(resolve, delay));

      const { width, height } =
        this.viewContainer.nativeElement.getBoundingClientRect();

      const png = await this.saveViewAsImageService.convertViewToImage(
        this.svg.nativeElement,
        width,
        height
      );

      if (png) {
        const path = await this.modelExplorerService.get(['organizations', id]);
        zip.file(`${path}/${view.name}.png`, png);
      }
    }

    const [batch, { name: projectName }, branch, version] = await Promise.all([
      zip.generateAsync({ type: 'blob' }),
      this.projectService.getCurrentProject(),
      this.modelService.get('branch', { includeFalsy: true }),
      this.modelService.get('version', { includeFalsy: true }),
    ]);

    saveAsFile(
      batch,
      `${projectName} ${branch} ${new Date(version).toUTCString()}.zip`
    );

    this.modelviewService.viewId = currentViewId;
    this.zoom.setZoom(zoomLevel);
  }

  async saveViewAsImage() {
    const zoomLevel = this.zoom.resetZoom();
    const { width, height } =
      this.viewContainer.nativeElement.getBoundingClientRect();

    await this.saveViewAsImageService.saveViewAsImage(
      this.svg.nativeElement,
      width,
      height
    );

    this.zoom.setZoom(zoomLevel);
  }

  @Input()
  set bucketMapping(bucketMapping: Dictionary<string>) {
    this.colorViewService.update({
      description: 'New bucket mapping available',
      payload: { bucketMapping },
    });
  }

  @Input()
  set highlightedEntity(guid: string) {
    this.modelExplorerService.highlihghtedEntity = guid;
  }

  @Input()
  set pallette(colorPallette: ColorPallette) {
    this.colorViewService.update({
      description: 'New palette available',
      payload: { colorPallette },
    });
  }

  @Input()
  set isPalletteFixed(isPalletteFixed: boolean) {
    this.colorViewService.update({
      description: `Palette set to fixed: ${Boolean(isPalletteFixed)
        .toString()
        .toUpperCase()}`,
      payload: { isPalletteFixed },
    });
  }

  @ViewChild(SVGZoomDirective, { static: false })
  set zoom(zoom: SVGZoomDirective) {
    this._zoom = zoom;
    if (zoom) {
      this.modelviewService
        .select('viewId')
        .pipe(untilDestroyed(zoom))
        .subscribe(() => this.resetZoom());
    }
  }

  get zoom() {
    return this._zoom;
  }
}
