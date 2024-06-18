import { Component, Input } from '@angular/core';
import { ModelElement } from '../../../parsers';

@Component({
  selector: 'models4insight-model-browser-element-row',
  templateUrl: 'model-browser-element-row.component.html',
  styleUrls: ['model-browser-element-row.component.scss'],
})
export class ModelBrowserElementRowComponent {
  @Input() entity: ModelElement;
}
