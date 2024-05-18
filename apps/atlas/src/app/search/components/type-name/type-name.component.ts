import { Component, Input } from '@angular/core';
import { iconsByType } from '../../meta';

@Component({
  selector: 'models4insight-type-name',
  templateUrl: 'type-name.component.html',
  styleUrls: ['type-name.component.scss'],
})
export class TypeNameComponent {
  /**
   * Whether or not to display the base type in parentheses when a type alias is given.
   */
  @Input() showBaseTypeName = false;

  /**
   * Whether or not to display the type icon.
   */
  @Input() showIcon = true;

  /**
   * Whether or not to display the type name or type alias.
   */
  @Input() showTypeName = true;

  /**
   * Overrides the given type name with a display name when shown on the page.
   */
  @Input() typeAlias: string;

  /**
   * The name of the entity type.
   */
  @Input() typeName: keyof typeof iconsByType;

  /**
   * Index of display properties per entity type.
   */
  protected readonly iconsByType = iconsByType;
}
