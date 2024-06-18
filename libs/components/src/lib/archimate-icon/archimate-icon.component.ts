import { Component, Input } from '@angular/core';
import { archimate3 } from '@models4insight/metamodel';
import { definitions, IconDefinition } from './definitions';

@Component({
  selector: 'models4insight-archimate-icon, [models4insight-archimate-icon]',
  templateUrl: 'archimate-icon.component.html',
  styleUrls: ['archimate-icon.component.scss'],
})
export class ArchimateIconComponent {
  private _iconDefinition: IconDefinition;
  private _type: keyof typeof archimate3.elements;

  @Input() set type(type: keyof typeof archimate3.elements) {
    this._iconDefinition = definitions[type];
    this._type = type;
  }

  get iconDefinition() {
    return this._iconDefinition;
  }

  get type() {
    return this._type;
  }
}
