import { Component, EventEmitter, Input, Output } from '@angular/core';

export type ColorPickerPosition =
  | 'top-left'
  | 'top-right'
  | 'bottom-left'
  | 'bottom-right';

@Component({
  selector: 'models4insight-color-square',
  templateUrl: 'color-square.component.html',
  styleUrls: ['color-square.component.scss'],
})
export class ColorSquareComponent {
  /**
   * Emits an event whenever the user picks a color
   */
  @Output() readonly colorChanged = new EventEmitter<string>();

  /**
   * Whether or not the color picker should be enabled
   */
  @Input() enableColorPicker = true;

  /**
   * The current color as a hex value
   */
  @Input() color: string;

  /**
   * The position of the color picker relative to the square
   */
  @Input() position: ColorPickerPosition = 'top-left';

  handleColorPickerChange(color: string) {
    this.colorChanged.emit(color);
  }
}
