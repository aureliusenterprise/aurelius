import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  ArchimateIconModule,
  FuzzySearchInputModule,
  QuickviewModule,
  SelectModule,
  SortableTableModule,
  SortableTableShellModule,
  TreeModule,
  ColorSquareModule,
} from '@models4insight/components';
import {
  DynamicComponentModule,
  IntersectionObserverModule,
  TooltipModule,
} from '@models4insight/directives';
import { ModelBrowserBrowseComponent } from './model-browser/browse/browse.component';
import { ViewSelectComponent } from './model-browser/browse/view-select/view-select.component';
import { ModelBrowserComponent } from './model-browser/model-browser.component';
import { ModelBrowserModelComponent } from './model-browser/model/model.component';
import { ModelBrowserSelectionComponent } from './model-browser/selection/selection.component';
import { ModelBrowserViewComponent } from './model-browser/view/view.component';
import { ModelviewComponent } from './modelview.component';
import { ModelviewConnectionComponent } from './shapes/connection/modelview-connection.component';
import { ModelviewNodeComponent } from './shapes/node/modelview-node.component';
import { SVGZoomDirective } from './svg-zoom.directive';
import { ModelBrowserEntitiesTableComponent } from './model-browser/model-browser-entities-table/model-broser-entities-table.component';
import { ModelBrowserElementRowComponent } from './model-browser/model-browser-entities-table/element/model-browser-element-row.component';
import { ModelBrowserRelationshipRowComponent } from './model-browser/model-browser-entities-table/relationship/model-browser-relationship-row.component';
import { PalletteSelectComponent } from './model-browser/view/pallette-select/pallette-select.component';

@NgModule({
  imports: [
    ArchimateIconModule,
    ColorSquareModule,
    CommonModule,
    DynamicComponentModule,
    FontAwesomeModule,
    FuzzySearchInputModule,
    IntersectionObserverModule,
    QuickviewModule,
    SelectModule,
    SortableTableModule,
    SortableTableShellModule,
    TooltipModule,
    TreeModule,
  ],
  declarations: [
    ModelBrowserComponent,
    ModelBrowserBrowseComponent,
    ModelBrowserElementRowComponent,
    ModelBrowserEntitiesTableComponent,
    ModelBrowserModelComponent,
    ModelBrowserSelectionComponent,
    ModelBrowserRelationshipRowComponent,
    ModelBrowserViewComponent,
    ModelviewComponent,
    ModelviewNodeComponent,
    ModelviewConnectionComponent,
    PalletteSelectComponent,
    SVGZoomDirective,
    ViewSelectComponent,
  ],
  exports: [ModelviewComponent],
})
export class Modelview2Module {}
