import { Directive, HostBinding, Input } from '@angular/core';

export type TooltipDirection = 'bottom' | 'left' | 'right' | 'top';

const directionClassMapping: {
  [direction in TooltipDirection]: string;
} = {
  bottom: 'has-tooltip-bottom',
  left: 'has-tooltip-left',
  right: 'has-tooltip-right',
  top: 'has-tooltip-top',
};

@Directive({
  exportAs: 'models4insight-tooltip',
  selector: 'models4insight-tooltip, [models4insight-tooltip]',
})
export class TooltipDirective {
  @HostBinding('attr.data-tooltip')
  @Input('models4insight-tooltip')
  tooltip: string;

  @HostBinding('class.tooltip')
  classTooltip = true;

  @HostBinding('class')
  tooltipDirectionClass = 'has-tooltip-left';

  @HostBinding('class.has-tooltip-multiline')
  @Input()
  isTooltipMultiline = false;

  @Input() set tooltipDirection(direction: TooltipDirection) {
    this.tooltipDirectionClass = directionClassMapping[direction];
  }
}
